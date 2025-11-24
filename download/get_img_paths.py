import os
import pandas as pd

root = '../data/imgs'

d = {
    'uuid': [],
    'path': []
}

for item in os.listdir(root):
    folder_path = os.path.join(root, item)

    if os.path.isdir(folder_path):  # ignore files at this level
        for fname in os.listdir(folder_path):
            if fname.lower().endswith('.jpeg'):  # only jpeg files
                img_path = os.path.join(folder_path, fname)
                uuid = os.path.splitext(fname)[0]

                d['uuid'].append(uuid)
                d['path'].append(img_path)

df = pd.DataFrame.from_dict(d)
df.to_csv('../data/img_paths.csv', index=False)