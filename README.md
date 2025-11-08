# Geo-Guessrs

A project using the Global Streetscapes dataset for geographic guessing games.

## Quick Links

- **Homepage**: https://ual.sg/project/global-streetscapes/
- **Dataset**: https://huggingface.co/datasets/NUS-UAL/global-streetscapes
- **Metadata**: https://huggingface.co/datasets/NUS-UAL/global-streetscapes/tree/main/data
- **Code Repository**: https://github.com/ualsg/global-streetscapes?tab=readme-ov-file

## About the Dataset

Global Streetscapes provides 10 million street-level images from 688 cities worldwide, enriched with 300+ attributes including geographic, temporal, and contextual metadata.

**Coordinate Ranges:**
- Latitude: -90 to 90
- Longitude: -180 to 180

## Setup

### 1. Install Dependencies

Create a virtual environment and install required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

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
