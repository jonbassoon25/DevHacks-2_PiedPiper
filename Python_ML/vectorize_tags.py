import numpy as np

df = np.array(np.load("./Python_ML/location_tags.npy", allow_pickle=True))


tags = set()
for tags_ in df:
	for tag_ in tags_:
		tags.add(tag_)

tags = np.array(list(tags), dtype=str)

vectors = np.zeros(shape=(df.shape[0], tags.shape[0]), dtype=np.int8)
for i in range(vectors.shape[0]):
	for j in range(vectors.shape[1]):
		if tags[j] in df[i]:
			vectors[i][j] = 1
		else:
			vectors[i][j] = 0

np.save("./location_tag_vectors.npy", vectors, True)
