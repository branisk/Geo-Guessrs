# Geo-Guessrs

## Quick Links

- **Homepage**: https://ual.sg/project/global-streetscapes/
- **Dataset**: https://huggingface.co/datasets/NUS-UAL/global-streetscapes
- **Metadata**: https://huggingface.co/datasets/NUS-UAL/global-streetscapes/tree/main/data
- **Code Repository**: https://github.com/ualsg/global-streetscapes?tab=readme-ov-file

## Local environment setup using virtual environment

Create a virtual environment and install required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Remote environment setup using runpod and conda

### Set up a pod

- Create a volume witih 150GB of space in a region that has your desired GPUs available. We used an A40 GPU.
- Use the following pod template: `Runpod Pytorch 2.4.0 runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- Configure the pod with your volume and your desired GPU (we used A40).

### Set up conda
- `cd /workspace` - this is the folder that will persist even if you terminate a pod (to save money between sessions)
- Download miniconda: `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`
- Install miniconda: `bash Miniconda3-latest-Linux-x86_64.sh`
    - As you go through the wizard, when prompted, tell the installer wizard to install conda in /workspace/miniconda
    - When asked whether to update your shell profile to automatically initialize conda, say no.
- Register the conda command line tool: `source /workspace/miniconda/etc/profile.d/conda.sh`
- Create a conda environment as per the environment.yaml file: `conda env create -f environment.yaml`
- Initialize conda: `conda init`
- Execute the steps in the section below (Run these commands each time you start a new pod)

### Run these commands each time you start a new pod:
- Register the conda command line tool: `source /workspace/miniconda/etc/profile.d/conda.sh`
- Activate your environment: `conda activate geoguessr`
- Register the conda kernel so that you can run Jupyter notebooks in that kernel: `python -m ipykernel install --user --name geoguessr --display-name "Python (geoguessr)"`
- Verify that the conda kernel was suggessfully registered: `jupyter kernelspec list`
- Configure git to save your credentials so you don't have to input your credentials each time you want to interact with github: `git config --global credential.helper store`

## Download data

### 1. Configure Mapillary Access

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

### 5. Download image coordinates

#### Option 1: Download from google drive
- If you are working with washington DC specifically, you can simply download the points.csv file here: https://drive.google.com/file/d/1DnWRgtedBkLx2SmhxoCUnLusRbAolxX_/view?usp=sharing

#### Option 2: Download using the mapillary API
- If you want to download the exact coordinates of exactly the images in your sampled.csv file, `python download/download_mly_points_using_sampled_csv.py`

#### Option 3: Download using mapillary sdk
- If you just want the coordinates of some images in some set of cities, use the `download/download_mly_points.py` script. There will be some overlap with the images in your sampled.csv file, but not full overlap.

### 5. Save the image paths

1. Open `/data/get_img_paths.ipynb`
2. Run all cells to generate `/data/img_paths.csv`

This file will be used during training and inference to find image paths

### 7. Create labels using Adaptive Partitioning

The primary paper outlining this partitioning can be found below in section 3 labeled "Adaptive Partitioning using S2 Cells":
- https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45488.pdf

1. Open `/data/adaptive_partition.ipynb`
2. Run all cells to add a "label" column to `/data/imgs/sampled.csv`

## Training

Sample code for loading data, training, and inference can be found at `/models/vit_b_16_base`.
Each iteration of the training epoch will save a pth file in the same directory.