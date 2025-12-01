import pandas as pd
import os

# the city information is available in the `simplemaps.csv` file
# https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/simplemaps.csv?download=true
df_all = pd.read_csv(
    "../data/simplemaps.csv", low_memory=False
)  # update the location of the desired csv file

city_id = 1840006060 # ID for Washington DC
df_subset = pd.DataFrame().reindex_like(df_all)
df_subset = df_all[df_all["city_id"] == city_id]

# load contextual information
# https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/contextual.csv?download=true
df_contextual = pd.read_csv("../data/contextual.csv", low_memory=False)

# merge our filtered dataset with contextual data
df_subset_merged = df_subset.merge(df_contextual, on=["uuid", "source", "orig_id"])

# filter only the rows during `day`
df_subset_merged = df_subset_merged[df_subset_merged["lighting_condition"] == "day"]
df_subset_merged["lighting_condition"].unique()

# keep the three required columns
df_to_download = df_subset_merged[["uuid", "source", "orig_id", "city", "country", "iso3"]]

# Ensure the directory exists
os.makedirs("../data/imgs", exist_ok=True)

# save the df_subset_merged
df_to_download.to_csv("../data/imgs/sampled.csv")