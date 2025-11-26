import pandas as pd

# the city information is available in the `simplemaps.csv` file
# https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/simplemaps.csv?download=true
df_all = pd.read_csv(
    "../data/simplemaps.csv"
)  # update the location of the desired csv file

cities = ["Washington"]
sample_size = 200000 # per city
df_subset = pd.DataFrame().reindex_like(df_all)
for city in cities:
    df_sample = df_all[df_all["city"] == city].sample(sample_size, replace=False, random_state=42)
    df_subset = pd.concat([df_subset, df_sample], ignore_index=True)

# load contextual information
# https://huggingface.co/datasets/NUS-UAL/global-streetscapes/resolve/main/data/contextual.csv?download=true
df_contextual = pd.read_csv("../data/contextual.csv")

# merge our filtered dataset with contextual data
df_subset_merged = df_subset.merge(df_contextual, on=["uuid", "source", "orig_id"])
df_subset_merged['count_per_country'] = df_subset_merged.groupby("country").transform("size")

# add int city label
city_to_int = {city: i for i, city in enumerate(sorted(cities))}
df_subset_merged["label"] = df_subset_merged["city"].map(city_to_int).astype("int64")

# keep the three required columns
df_to_download = df_subset_merged[["uuid", "source", "orig_id", "city_lat", "city_lon", "city", "country", "count_per_country", "iso3"]]
# save the file
df_to_download.to_csv("../data/imgs/sampled.csv")