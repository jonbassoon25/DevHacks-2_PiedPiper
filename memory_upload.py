from supermemory import Supermemory
import os

client = Supermemory(api_key="sm_7v34ad1Mm5XeKoiM2gNd2V_IZMERieGyPMWxXBJEeoiTNLeVyBKFznTiBielvymJErPcdiCrXTlXDevMqWYKirP")

import pandas as pd
import csv

# Read CSV file
df = pd.read_csv('location_database.csv')

# Convert to text format
csv_content = df.to_string()  # or df.to_csv()

# Add to Supermemory
client.memories.add(
    content=csv_content,
    container_tags=["csv_data"],
    metadata={"source": "csv_file", "filename": "your_file.csv"}
)