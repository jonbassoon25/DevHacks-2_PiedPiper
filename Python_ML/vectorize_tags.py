import numpy as np

df = np.array(np.load("./Python_ML/location_tags.npy", allow_pickle=True))


tags = set()
for tags_ in df:
	for tag_ in tags_:
		tags.add(tag_)

print(tags)