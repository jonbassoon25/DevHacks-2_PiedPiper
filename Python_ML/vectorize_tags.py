import numpy as np

df = np.load("location_tags.npy", allow_pickle=True)

tags = df.flatten()
tags = np.array(tags)

print(tags)