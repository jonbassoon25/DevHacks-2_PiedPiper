import numpy as np
import csv, math

# Import tags
df = np.array(np.load("./Python_ML/location_tags.npy", allow_pickle=True))

tags = set()
for tags_ in df:
	for tag_ in tags_:
		tags.add(tag_)

tags = np.array(list(tags), dtype=str)

# Vectorize tags
vectors = np.zeros(shape=(df.shape[0], tags.shape[0] + 1), dtype=np.uint8)
for i in range(vectors.shape[0]):
	for j in range(vectors.shape[1] - 1):
		if tags[j] in df[i]:
			vectors[i][j] = 1
		else:
			vectors[i][j] = 0

# Add ratings from 0 - 255 ( rating * ( 255 / 5)  * ((1/(-rating/10)-1) + 1) )
with open("./location_database.csv") as csvFile:
	count = 0
	for line in csv.reader(csvFile):
		if (count == 0):
			count += 1
			continue
		rating = float(line[2])
		reviews = int(line[3])
		vectors[count - 1][vectors.shape[1] - 1] = math.trunc(rating * 51 * (( 1 / (-(reviews / 10) - 1) ) + 1))
		
		count += 1


np.save("./Python_ML/location_vectors.npy", vectors, True)

print("\n".join(map(str, list(vectors))))