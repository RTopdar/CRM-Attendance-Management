# lib/db.py
from datetime import datetime, timedelta
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import pandas as pd

import os
import atexit

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# Initialize MongoDB client and database
client = None
db = None

try:

    client = MongoClient(MONGO_URI)
    db = client["Attendance_DB"]
    print("Successfully connected to MongoDB.")
except errors.ConnectionError as e:
    print(f"Failed to connect to MongoDB: {e}")


def get_db():
    return db


def close_connection():
    if client:
        client.close()
        print("MongoDB connection closed.")

import bcrypt

def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def create_user(username, email, password):
    db = get_db()
    # Check if the user already exists
    if db["Users"].find_one({"username": username}):
        return {"message": "User already exists."}
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Create the user document
    user = {
        "username": username,
        "email": email,
        "password": hashed_password
    }
    
    # Insert the user into the database
    db["Users"].insert_one(user)
    return {"message": "User created successfully."}

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def login_user(username, password):
    db = get_db()
    user = db["Users"].find_one({"username": username})
    if user and verify_password(user["password"], password):
        return {"message": "Login successful."}
    else:
        return {"message": "Invalid username or password."}










# Create a Worker Schema that Fetches Teh Worker List from Mongo and Then Creates a New Dictionary with the Worker ID and Worker Name


def create_Worker_Schema():
    db = get_db()
    # Fetch all entries from the Worker_Data collection
    entries = list(db["Worker_Data"].find())

    worker_schema = []

    for entry in entries:
        worker_schema.append(
            {
                "Worker_ID": str(entry["_id"]),
                "Worker_Name": entry["NAME"],
                "Worker_Email": entry["EMAIL"],
                "Worker_Phone": entry["PHONE"] if "PHONE" in entry else "",
                "Comments": "",
                "STATUS": "",
            }
        )

    return worker_schema


# Create a new Attendance Entry
def create_Attendance_Entry(date=None):
    print(f"Creating Attendance Entry at {date}")
    db = get_db()
    current_time = datetime.now()
    ist_time = current_time + timedelta(hours=5, minutes=30)
    ist_date = ist_time.date()
    ist_iso_format = ist_date.isoformat()
    date_info = None
    if date is not None:
        print("Date is provided.")
        date_info = date
    else:
        print("Date is not provided.")
        date_info = ist_iso_format

    entry = db["Daily_Attendance"].find_one({"DATE": date_info})

    if entry is not None:
        print("Attendance entry already exists.")
        entry["_id"] = str(entry["_id"])
        return entry
    elif entry is None:
        print("Attendance entry does not exist.")
        workers = create_Worker_Schema()
        attendance = {
            "DATE": date_info,
            "WORKER_LIST": workers,
            "CLIENT_ID": "",
            "SIGNED_BY": "",
        }
        result = db["Daily_Attendance"].insert_one(attendance)
        print("Attendance entry created successfully.")
        new_entry = db["Daily_Attendance"].find_one({"_id": result.inserted_id})
        new_entry["_id"] = str(new_entry["_id"])
        return new_entry


# Update the Attendance Entry
def update_attendance_entry(DATE, WORKER_DATA):
    present = 0
    absent = 0
    db = get_db()
    entry = db["Daily_Attendance"].find_one({"DATE": DATE})
    if entry is None:
        return "Attendance Entry does not exist."
    for data in WORKER_DATA:
        if data["STATUS"] == "PRESENT":
            present += 1
        elif data["STATUS"] == "ABSENT":
            absent += 1
    db["Daily_Attendance"].update_one(
        {"DATE": DATE},
        {
            "$set": {
                "WORKER_LIST": WORKER_DATA,
                "PRESENT": present,
                "ABSENT": absent,
            }
        },
    )
    return "Attendance Entry Updated Successfully"

# Return All Attendance Entries
def get_all_attendance_entries():
    db = get_db()
    entries = list(db["Daily_Attendance"].find())
    for entry in entries:
        entry["_id"] = str(entry["_id"])
    return entries

# Return all worker data
def get_all_worker_data():
    db = get_db()
    entries = list(db["Worker_Data"].find())
    for entry in entries:
        entry["_id"] = str(entry["_id"])
    return entries

# Get entry of a date and convert the json to downloadable csv

import pandas as pd
import os

def generate_csv_report(date):
    print(f"Generating Report for {date}")
    db = get_db()
    report = db["Daily_Attendance"].find_one({"DATE": date})
    if report is None:
        return {"message": "Report not found."}

    worker_list = report["WORKER_LIST"]
    absent = report["ABSENT"]
    present = report["PRESENT"]

    # Prepare the worker data
    for worker in worker_list:
        worker["Name"] = worker.pop("Worker_Name")
        worker["Email"] = worker.pop("Worker_Email")
        worker["Status"] = worker.pop("STATUS")
        worker["Phone"] = worker.pop("Worker_Phone")
        worker.pop("Worker_ID", None)

    # Create a DataFrame for the worker list
    df = pd.DataFrame(worker_list, columns=["Name", "Email", "Status"])

    # Create a single-row DataFrame for presentee and absentee counts
    summary_df = pd.DataFrame([{
        "Name": "", 
        "Email": "", 
        "Status": "", 
        "Phone": "",
        "Presentee": present, 
        "Absentee": absent,
        "Date": date
    }])

    # Add the new columns for presentee and absentee counts to the worker DataFrame
    df["Presentee"] = ""
    df["Absentee"] = ""

    # Concatenate the worker DataFrame with the summary row
    df = pd.concat([df, summary_df], ignore_index=True)

    # Convert the DataFrame to CSV
    csv_data = df.to_csv(index=False)

    # Save the CSV to a local file
    csv_file_path = f"attendance_report_{date}.csv"
    with open(csv_file_path, 'w') as file:
        file.write(csv_data)

    print(f"CSV report saved to {csv_file_path}")

    return csv_data


if __name__ == "__main__":
    # Test the connection
    if db is not None:
        print("Database connection is active.")
    else:
        print("Database connection is not active.")

    create_Attendance_Entry()
