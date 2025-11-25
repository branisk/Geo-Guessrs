import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict
from s2sphere import CellId, LatLng, Cell

# http://s2geometry.io/about/overview
# http://s2geometry.io/devguide/s2cell_hierarchy.html
def adaptive_partition(df: pd.DataFrame, t1: int = 10_000, t2: int = 50, max_level: int = 18):
    all_cells = defaultdict(list)
    
    # Loop through all lat,lon values
    for _, row in df.iterrows():
        lat, lon = row['lat'], row['lon']
        latlng = LatLng.from_degrees(lat, lon)
        cell_id = CellId.from_lat_lng(latlng)
        
        # Add the lat,lon to be cells at each hierarchy
        for level in range(max_level + 1):
            parent = cell_id.parent(level)
            all_cells[parent.id()].append((lat, lon))
            
    final_cells = set()
    processed = set()
    
    def recurse(cell_id_val: CellId, depth: int):
        """Recursive function to calculate and slice cells of the grid"""
        # Cell already processed
        if cell_id_val in processed:
            return
        processed.add(cell_id_val)
        
        points_list = all_cells.get(cell_id_val, [])
        # No points exist in the cell
        if len(points_list) == 0:
            return
            
        # Not big enough to split or done splitting
        if len(points_list) <= t1 or depth >= max_level:
            # Only keep cells that contain enough points
            if len(points_list) >= t2:
                final_cells.add(cell_id_val)
            return
        
        # Too many points, recurse through each split of the cell
        cell_id_obj = CellId(cell_id_val)
        for i in range(4):
            child = cell_id_obj.child(i)
            recurse(child.id(), depth + 1)
    
    # Iterate through each level and recurve through the cells
    for level in range(max_level + 1):
        level_cells = [cid for cid in all_cells.keys() if CellId(cid).level() == level]
        for cell_id_val in level_cells:
            if cell_id_val not in processed:
                recurse(cell_id_val, level)
    
    return final_cells

def get_cell_vertices(cell_id_val: CellId):
    """Grabs all 4 vertices of a cell"""
    cell_id_obj = CellId(cell_id_val)
    cell = Cell(cell_id_obj)
    vertices = []
    for i in range(4):
        vertex = cell.get_vertex(i)
        latlng = LatLng.from_point(vertex)
        vertices.append((latlng.lat().degrees, latlng.lng().degrees))
    return vertices

def latlon_to_cellid(lat: float, lon: float):
    """Find which final cell this lat/lon belongs to"""
    latlng = LatLng.from_degrees(lat, lon)
    cell_id = CellId.from_lat_lng(latlng)
    
    # Traverse from max_level down to find the corresponding cell
    # Each lat,lon only belongs to the highest level cell
    for level in range(max_level, -1, -1):
        parent = cell_id.parent(level)
        parent_id = parent.id()
        
        if parent_id in final_cells:
            return parent_id
    
    return None
if __name__=="__main__":
    max_level = 25
    t1 = 100
    t2 = 5
    
    sampled_df = pd.read_csv('../data/imgs/sampled.csv', index_col=0)
    if 'lat' in sampled_df.columns and 'lon' in sampled_df.columns:
        sampled_df = sampled_df.drop(columns=['lat', 'lon'])
    points_df = pd.read_csv('../data/points.csv')
    points_df = points_df.rename(columns={'id': 'orig_id'})
    points_df = points_df[['orig_id', 'lat', 'lon']]
    city_df = pd.merge(sampled_df, points_df, on=['orig_id'])
    
    final_cells = adaptive_partition(city_df, t1=t1, t2=t2, max_level=max_level)

    # Add the cell id corresponding to each latitude and longitude
    city_df['s2_cell_id'] = city_df.apply(
        lambda row: latlon_to_cellid(row['lat'], row['lon']), 
        axis=1
    )

    # Remove null cell_ids
    city_df.dropna(subset=['s2_cell_id'], inplace=True)
    cell_ids = [int(id) for id in set(city_df['s2_cell_id'].unique())]
    
    replacement_dict = dict()
    for i, cell_id in enumerate(cell_ids):
        replacement_dict[cell_id] = i
        
    city_df['label'] = city_df['s2_cell_id'].replace(replacement_dict).astype(int)
    city_df.to_csv('../data/imgs/sampled.csv')
    