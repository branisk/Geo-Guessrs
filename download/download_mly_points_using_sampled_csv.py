"""
This script contains functions to be imported to raw_download.py, but it can also be run 
on its own to download Mapillary SVIs (metadata only).

Two modes of operation:
1. City-based: Takes a list of city ID(s) and downloads all images from the level-14 vector tile 
   associated with each input city's location.
2. Image ID-based: Takes a CSV file (sampled.csv) with an 'orig_id' column containing Mapillary 
   image IDs and fetches lat/lon coordinates for those specific images.

Input: 
- City mode: a list of city ID(s) - please specify in the variable 'targets' below
- Image ID mode: a CSV file called 'sampled.csv' with an 'orig_id' column

Output: one CSV file containing the metadata of all downloaded Mapillary SVI

Note: 
- Please register for a free access token from Mapillary and insert it in the 'access_token' variable below
- If encounter network error, please try running the script again as the API connection is not always stable
"""

import mapillary.interface as mly
import pandas as pd
import geopandas as gp
import os
from pathlib import Path
import datetime
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# Global access token for direct API calls
ACCESS_TOKEN = None

# Number of parallel workers (adjust based on rate limits)
NUM_WORKERS = 50


def filter_date(df, start_date, end_date):
    # create a temporary column date from captured_at (milliseconds from Unix epoch)
    df["date"] = pd.to_datetime(df["captured_at"], unit="ms")
    # check if start_date and end_date are in the correct format with regex. If not, raise error
    if start_date is not None:
        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect start_date format, should be YYYY-MM-DD")
    if end_date is not None:
        try:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect end_date format, should be YYYY-MM-DD")
    # if start_date is not None, filter out the rows with date < start_date
    df = (
        df[df["date"] >= start_date] if start_date is not None else df
    )
    # if end_date is not None, filter out the rows with date > end_date
    df = df[df["date"] <= end_date] if end_date is not None else df
    # drop the temporary column date
    df = df.drop(columns="date")
    return df

def get_mly_gdf(city, start_date, end_date):
    """
    Download data from Mapillary and return as a geodataframe.
    """
    cityname = city['city']
    print(f'Downloading Mapillary data for {cityname}...')
    lon = city['lng']
    lat = city['lat']
    try:
        data = mly.get_image_close_to(longitude=lon, latitude=lat)
        dict_data = data.to_dict()
        gdf = gp.GeoDataFrame.from_features(dict_data)
        if not gdf.empty:
            print('Filtering data based on specified time period...')
            gdf = filter_date(gdf, start_date, end_date)
            gdf['city_id'] = [city['id']] * len(gdf)
            gdf['lat'] = gdf.geometry.y
            gdf['lon'] = gdf.geometry.x
            nSeqs = gdf['sequence_id'].nunique()
            print(f'Download complete, collected', nSeqs, 'sequences', len(gdf), 'points')
        return gdf
        # ls_gdf.append(gdf)
    except Exception as e:
        print('network error', e)
        print('No Mapillary data found for', city['city'])


def save_csv(gdf, city, save_folder):
    """
    Save the geodataframe into a csv.
    """
    filename = 'points.csv'
    dst_path = os.path.join(save_folder, filename)
    pd.DataFrame(gdf.drop(columns='geometry')).to_csv(dst_path, index=False)
    print('Downloaded Mapillary points for', city['city'])


def download_mly_csv(city, save_folder, start_date, end_date):
    gdf = get_mly_gdf(city, start_date, end_date)
    save_csv(gdf, city, save_folder)


def check_id(save_folder):
    """
    Check the save directory for any cities that have already been downloaded to skip download for them.
    """
    ids = set()
    for name in os.listdir(save_folder):
        if name != '.DS_Store':
            ids.add(name.split('_')[1].split('.')[0])
    return ids


def get_image_coords(image_id, max_retries=3):
    """
    Fetch the coordinates (lat/lon) for a specific Mapillary image ID.
    Uses direct API calls to graph.mapillary.com for reliability.
    Returns a dict with 'id', 'lat', 'lon' or None if failed.
    """
    global ACCESS_TOKEN
    
    # Valid fields according to Mapillary API v4 documentation:
    # geometry, captured_at, compass_angle, is_pano, sequence
    fields = 'geometry,captured_at,compass_angle,is_pano,sequence'
    url = f'https://graph.mapillary.com/{int(image_id)}?fields={fields}'
    headers = {'Authorization': f'OAuth {ACCESS_TOKEN}'}
    
    for attempt in range(max_retries):
        try:
            # Minimal delay - API allows 60k requests/min
            time.sleep(0.01)
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle geometry field
                if 'geometry' in data and data['geometry']:
                    coords = data['geometry'].get('coordinates', [])
                    if len(coords) >= 2:
                        return {
                            'id': image_id,
                            'lon': coords[0],
                            'lat': coords[1],
                            'captured_at': data.get('captured_at'),
                            'compass_angle': data.get('compass_angle'),
                            'is_pano': data.get('is_pano'),
                            'sequence_id': data.get('sequence')
                        }
            elif response.status_code == 404:
                # Image not found - don't retry
                return None
            elif response.status_code == 429:
                # Rate limited - wait and retry
                time.sleep(2)
                continue
            else:
                raise Exception(f'API returned status {response.status_code}')
                
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Brief wait before retry
            else:
                return None
    return None


def get_coords_from_sampled_csv(sampled_csv_path, save_folder):
    """
    Read a CSV file with 'orig_id' column containing Mapillary image IDs,
    fetch lat/lon for each using parallel processing, and save results to points.csv.
    """
    print(f'Reading sampled CSV from {sampled_csv_path}...')
    sampled_df = pd.read_csv(sampled_csv_path)
    
    if 'orig_id' not in sampled_df.columns:
        raise ValueError("sampled.csv must contain an 'orig_id' column")
    
    image_ids = list(sampled_df['orig_id'].unique())
    total = len(image_ids)
    print(f'Found {total} unique image IDs to process...')
    print(f'Using {NUM_WORKERS} parallel workers...')
    
    results = []
    failed_count = 0
    start_time = time.time()
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Submit all tasks
        future_to_id = {executor.submit(get_image_coords, img_id): img_id for img_id in image_ids}
        
        completed = 0
        for future in as_completed(future_to_id):
            completed += 1
            result = future.result()
            
            if result:
                results.append(result)
            else:
                failed_count += 1
            
            # Progress update every 500 images
            if completed % 500 == 0 or completed == total:
                elapsed = time.time() - start_time
                rate = completed / elapsed
                remaining = (total - completed) / rate if rate > 0 else 0
                print(f'Progress: {completed}/{total} ({100*completed/total:.1f}%) | '
                      f'Success: {len(results)} | Failed: {failed_count} | '
                      f'Rate: {rate:.1f}/sec | ETA: {remaining/60:.1f} min')
    
    # Save results
    if results:
        result_df = pd.DataFrame(results)
        filename = 'points.csv'
        dst_path = os.path.join(save_folder, filename)
        result_df.to_csv(dst_path, index=False)
        elapsed = time.time() - start_time
        print(f'\nComplete! Saved {len(results)} image coordinates to {dst_path}')
        print(f'Total time: {elapsed/60:.1f} minutes ({elapsed:.0f} seconds)')
        print(f'Failed to fetch: {failed_count} images')
    else:
        print('No coordinates were fetched successfully.')
    
    return results


if __name__ == '__main__':

    access_token = os.getenv('MAPILLARY_ACCESS_TOKEN')  # insert your access token here. access token can be registered on Mapillary for free.
    mly.set_access_token(access_token)
    
    # Set global access token for direct API calls
    ACCESS_TOKEN = access_token

    # ========== MODE SELECTION ==========
    # Set to True to use image ID mode (reads from sampled.csv)
    # Set to False to use city-based mode (uses targets list)
    USE_IMAGE_ID_MODE = True
    
    # directory to save the downloaded data
    save_folder = Path(__file__).parent / '../data' # please modify as needed
    Path(save_folder).mkdir(parents=True, exist_ok=True)

    if USE_IMAGE_ID_MODE:
        # ========== IMAGE ID MODE ==========
        # Read image IDs from sampled.csv and fetch their coordinates
        sampled_csv_path = Path(__file__).parent / '../data/imgs/sampled.csv'  # please modify as needed
        
        if not sampled_csv_path.exists():
            print(f'Error: sampled.csv not found at {sampled_csv_path}')
            print('Please create a sampled.csv file with an "orig_id" column containing Mapillary image IDs.')
        else:
            get_coords_from_sampled_csv(sampled_csv_path, save_folder)
            print('Done')
    
    else:
        # ========== CITY-BASED MODE ==========
        # for each of your chosen cities, find its ID from data/worldcities.csv.
        # remember to check the country information to make sure it's the city you want, as different cities can share the same name, e.g. 'San Francisco'.
        # the below city ids correspond to 'New York'
        targets = [1840006060] # THIS IS WASHINGTON DC

        start_date = None#'2024-04-01' # start date to download data - please modify as needed (start_date=None indicates download from the earliest available image)
        end_date = None # end date to download data - please modify as needed (end_date=None indicates download until the latest available image)

        # import the simplemaps worldcities database to get city centre for data download
        wc = pd.read_csv(Path(__file__).parent / '../data/worldcities.csv') # please modify as needed

        already_id = []#check_id(save_folder)
        total = len(targets)
        index = 0
        start_size = len([entry for entry in os.listdir(
            save_folder) if os.path.isfile(os.path.join(save_folder, entry))])
        
        cities = wc[wc['id'].isin(targets)]

        for _, city in cities.iterrows():

            if str(city['id']) in already_id:
                continue

            index += 1
            download_mly_csv(city, save_folder, start_date, end_date)
            print('Now:', index, total-len(already_id), 'already:', len(already_id))

        end_size = len([entry for entry in os.listdir(save_folder)
                       if os.path.isfile(os.path.join(save_folder, entry))])
        increase = end_size - start_size
        print('Number of cities with data:', increase, '/', total-len(already_id))
        print('Done')
