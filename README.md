# Geo-Guessrs

## Data
Homepage: https://ual.sg/project/global-streetscapes/
Dataset: https://huggingface.co/datasets/NUS-UAL/global-streetscapes
Metadata Tables: https://huggingface.co/datasets/NUS-UAL/global-streetscapes/tree/main/data
Repository: https://github.com/ualsg/global-streetscapes?tab=readme-ov-file
Download Instructions: https://github.com/ualsg/global-streetscapes/wiki/2-Download-images

Latitude: -90 -> 90
Longitude: -180 -> 180

## Development

Before any of the following steps, first create a virtual environment in the main directory and install the required packages. (For linux)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### Creating an access token

echo "MAPILLARY_ACCESS_TOKEN = ''" > download/.env
Obtain an access token by logging in to https://www.mapillary.com/app/, and navigating to https://www.mapillary.com/dashboard/developers and pressing "View" corresponding to "Acess Token".
Add this token to the previously created file at download/.env

### Downloading the sampled dataset

First, download the required files and place them in the /data directory. These files are 1.6GB and 1.16GB respectively.
- https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/simplemaps.csv?download=true
- https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/contextual.csv?download=true

Next, open and run the notebook /download/subset_download.ipynb. This creates the sample metadata file /data/imgs/sampled.csv.
Finally, navigate to /download and run download_jpegs.py. This will download the images to data/imgs, 10,000 images per bucket.