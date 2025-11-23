# Geo-Guessrs

## Quick Links

- **Homepage**: https://ual.sg/project/global-streetscapes/
- **Dataset**: https://huggingface.co/datasets/NUS-UAL/global-streetscapes
- **Metadata**: https://huggingface.co/datasets/NUS-UAL/global-streetscapes/tree/main/data
- **Code Repository**: https://github.com/ualsg/global-streetscapes?tab=readme-ov-file

**Coordinate Ranges:**
- Latitude: -90 to 90
- Longitude: -180 to 180

## Setup

### 1. Local setup (using venv)

Create a virtual environment and install required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 1. Run Pod setup (using conda)

#### A. Set up pod

1. Create a volume in the MTL region
2. Use the following pod template: Runpod Pytorch 2.4.0 runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
3. Connect the pod to the volume, pick the A40 GPU

#### B Set up conda
1. cd /workspace
2. wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
3. bash Miniconda3-latest-Linux-x86_64.sh
4. Tell the installer wizard to install conda in /workspace/miniconda
5. When asked whether to update your shell profile to automatically initialize conda, say no.
6. `source /workspace/miniconda/etc/profile.d/conda.sh`
7. `conda env create -f environment.yaml`
8. `conda init`
9. `conda activate geoguessr`
10. Register the conda kernel `python -m ipykernel install --user --name geoguessr --display-name "Python (geoguessr)"`

#### C Each time you initialize a pod
1. `source /workspace/miniconda/etc/profile.d/conda.sh`
2. `conda activate geoguessr`
3. Register the conda kernel `python -m ipykernel install --user --name geoguessr --display-name "Python (geoguessr)"`
4. `jupyter kernelspec list`
5. `git config --global credential.helper store`

### 2. Configure Mapillary Access

Create an environment file for your API token:

```bash
echo "MAPILLARY_ACCESS_TOKEN = ''" > download/.env
```

Get your token:
1. Log in at https://www.mapillary.com/app/
2. Go to https://www.mapillary.com/dashboard/developers
3. Click "View" next to "Access Token"
4. Paste the token into `download/.env`

### 3. Download Dataset Files

Download these two files (2.76GB total) and place them in the `/data` directory:

- simplemaps.csv (1.6GB): https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/simplemaps.csv?download=true
- contextual.csv (1.16GB): https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/contextual.csv?download=true

### 4. Sample and Download Images

**Create sample metadata:**
1. Open `/download/subset_download.ipynb`
2. Run all cells to generate `/data/imgs/sampled.csv`

**Download images:**

```bash
cd download
python download_jpegs.py
```

Images will be saved to `/data/imgs` in buckets of 10,000 images each.

### 5. Save the image paths

1. Open `/data/get_img_paths.ipynb`
2. Run all cells to generate `/data/img_paths.csv`

This file will be used during training and inference to find image paths

### 6. Create labels using Adaptive Partitioning

The primary paper outlining this partitioning can be found below in section 3 labeled "Adaptive Partitioning using S2 Cells":
- https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45488.pdf

1. Open `/data/adaptive_partition.ipynb`
2. Run all cells to save cell labels `/data/imgs/sampled.csv`

## Training

Sample code for loading data, training, and inference can be found at `/models/vit_b_16_base`.
Each iteration of the training epoch will save a pth file in the same directory.