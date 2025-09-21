import json, csv
import numpy as np

database = {}

with open("./location_database.csv") as csvFile:
	first = True
	for line in csv.reader(csvFile):
		if first:
			first = False
			continue
		database[line[0]] = line

with open("./location_database.json", 'w') as jsonFile:
	json.dump(database, jsonFile)