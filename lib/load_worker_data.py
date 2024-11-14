import pandas as pd
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

import os

print("Current Working Directory:", os.getcwd())

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["Attendance_DB"]

csv_file_path = os.path.abspath("schema/sample_attendance_data.csv")

df = pd.read_csv(csv_file_path)

collection = db["Worker_Data"]

records = df.to_dict(orient="records")

try:
    result = collection.insert_many(records)
    print(f"Inserted {len(result.inserted_ids)} records.")
    if client:
        client.close()
        print("MongoDB connection closed.")

except BulkWriteError as bwe:
    print(f"Error inserting data: {bwe.details}")
    if client:
        client.close()
        print("MongoDB connection closed.")
