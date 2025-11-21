import os
import pandas as pd

root = '../data/imgs/1_10000'
d = {
    'uuid': [],
    'path': []
}
for img in os.listdir(root):
    if img != '.DS_Store':
        uuid = img.split('.')[0]
        path = root + '/' + img
        d['uuid'].append(uuid)
        d['path'].append(path)
df = pd.DataFrame.from_dict(d)

df.to_csv('../data/img_paths.csv', index=False)