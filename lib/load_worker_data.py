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


def transform_worker_data(row):
    return {
        "NAME": {"DESCRIPTION": "Worker Name", "VALUE": row["NAME"]},
        "CITY": {"DESCRIPTION": "Worker City", "VALUE": row["CITY"]},
        "ASSIGNED_CLIENT_ID": {
            "DESCRIPTION": "Assigned Client",
            "VALUE": row["ASSIGNED_CLIENT_ID"],
        },
        "STATUS": {"DESCRIPTION": "Labourer Status", "VALUE": row["STATUS"]},
        "PHONE_NUMBER": {"DESCRIPTION": "Phone Number", "VALUE": row["PHONE_NUMBER"]},
        "EMAIL": {"DESCRIPTION": "Email", "VALUE": row["EMAIL"]},
    }


records = df.apply(transform_worker_data, axis=1).tolist()

collection = db["Worker_Data"]

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
