wget -nc "https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/contextual.csv" -O data/contextual.csv
wget -nc "https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/simplemaps.csv" -O data/simplemaps.csv
cd download
python subset_download.py
python download_jpegs.py
python download_mly_points.py
python get_img_paths.py
python adaptive_partition.py
cd ..