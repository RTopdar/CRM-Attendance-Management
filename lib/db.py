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
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def create_user(username, email, password):
    db = get_db()
    # Check if the user already exists
    if db["Users"].find_one({"username": username}):
        return {"message": "User already exists."}
    # Check if the email is already in use
    if db["Users"].find_one({"email ": email}):
        return {"message": "Email already in use."}

    # Hash the password
    hashed_password = hash_password(password)

    # Create the user document
    user = {"username": username, "email": email, "password": hashed_password}

    # Insert the user into the database
    db["Users"].insert_one(user)
    return {"message": "User created successfully."}


def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password)


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
                "WORKER_ID": str(entry["_id"]),
                "WORKER_NAME": entry["NAME"],
                "WORKER_EMAIL": entry["EMAIL"],
                "PHONE": entry["PHONE"] if "PHONE" in entry else "",
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



def update_client_attendance_entry(DATE, CLIENT_ID, ATTENDANCE_DATA):
    db = get_db()
    entry = db["Daily_Attendance"].find_one({"DATE": DATE})
    if entry is None:
        return "Attendance Entry does not exist."
    
    # Update the customer's attendance data
    result = db["Customers"].update_one(
        {"_id": ObjectId(CLIENT_ID)},
        {
            "$set": {
                f"ATTENDANCE_DATA.{DATE}": ATTENDANCE_DATA
            }
        }
    )
    
    if result.matched_count == 0:
        return "Customer not found."
    
    return "Client Attendance Entry Updated Successfully"

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
    print("Report Found", report["WORKER_LIST"])

    worker_list = report["WORKER_LIST"]

    # Filter out workers with status "ABSENT"
    worker_list = [
        worker for worker in worker_list if worker["STATUS"]["VALUE"] != "ABSENT"
    ]

    # Prepare the worker data
    for worker in worker_list:
        worker["Name"] = worker.pop("Worker_Name")
        worker["Email"] = worker.pop("Worker_Email")
        worker["Phone"] = worker.pop("Worker_Phone")
        worker.pop("Worker_ID", None)

    # Create a DataFrame for the worker list
    df = pd.DataFrame(worker_list, columns=["Name", "Email", "Phone"])

    # Convert the DataFrame to CSV
    csv_data = df.to_csv(index=False)

    # Save the CSV to a local file
    csv_file_path = f"attendance_report_{date}.csv"
    with open(csv_file_path, "w") as file:
        file.write(csv_data)

    print(f"CSV report saved to {csv_file_path}")

    return csv_data


def generate_new_client_response():
    csv_file_path = "schema/Attendance Schema - Client.csv"
    df = pd.read_csv(csv_file_path)

    client_data = {}
    for _, row in df.iterrows():
        field_name = row["VARIABLE NAME"]
        description = row["DESCRIPTION"]

        client_data[field_name] = {"DESCRIPTION": description, "VALUE": ""}
    # Get current time in IST
    import pytz

    ist = pytz.timezone("Asia/Kolkata")
    created_on_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S %Z%z")
    response = {"CREATED_ON": created_on_ist, "CUSTOMER_DATA": client_data}

    return response


#  Create a new customer


def create_customer():

    new_client_response = generate_new_client_response()
    return new_client_response


# SAVE CUSTOMER DATA
def save_new_customer_data(CUSTOMER_DATA):
    db = get_db()

    if CUSTOMER_DATA["CUSTOMER_DATA"]["NAME"]["VALUE"] == "":
        return {"MESSAGE": "CUSTOMER NAME IS REQUIRED."}
    if CUSTOMER_DATA["CUSTOMER_DATA"]["EMAIL"]["VALUE"] == "":
        return {"MESSAGE": "CUSTOMER EMAIL IS REQUIRED."}
    if CUSTOMER_DATA["CUSTOMER_DATA"]["MOBILE"]["VALUE"] == "":
        return {"MESSAGE": "CUSTOMER MOBILE IS REQUIRED."}

    check_entry = db["Customers"].find_one(
        {"CUSTOMER_DATA.EMAIL.VALUE": CUSTOMER_DATA["CUSTOMER_DATA"]["EMAIL"]["VALUE"]}
    )
    if check_entry is not None:
        return {"MESSAGE": "CUSTOMER EMAIL ALREADY EXISTS."}
    check_entry = db["Customers"].find_one(
        {
            "CUSTOMER_DATA.MOBILE.VALUE": CUSTOMER_DATA["CUSTOMER_DATA"]["MOBILE"][
                "VALUE"
            ]
        }
    )
    if check_entry is not None:
        return {"MESSAGE": "CUSTOMER MOBILE ALREADY EXISTS."}
    check_entry = db["Customers"].find_one(
        {"CUSTOMER_DATA.NAME.VALUE": CUSTOMER_DATA["CUSTOMER_DATA"]["NAME"]["VALUE"]}
    )
    if check_entry is not None:
        return {"MESSAGE": "CUSTOMER NAME ALREADY EXISTS."}

    result = db["Customers"].insert_one(CUSTOMER_DATA)
    new_entry = db["Customers"].find_one({"_id": result.inserted_id})
    new_entry["_id"] = str(new_entry["_id"])
    return {"MESSAGE": "CUSTOMER DATA SAVED SUCCESSFULLY.", "CUSTOMER_DATA": new_entry}


from bson import ObjectId


from bson import ObjectId

def update_customer_data(CUSTOMER_ID, CUSTOMER_DATA):
    db = get_db()

    if CUSTOMER_DATA["NAME"]["VALUE"] == "":
        return {"MESSAGE": "CUSTOMER NAME IS REQUIRED."}
    if CUSTOMER_DATA["EMAIL"]["VALUE"] == "":
        return {"MESSAGE": "CUSTOMER EMAIL IS REQUIRED."}
    if CUSTOMER_DATA["MOBILE"]["VALUE"] == "":
        return {"MESSAGE": "CUSTOMER MOBILE IS REQUIRED."}
    
    # Convert CUSTOMER_ID to ObjectId
    customer_id_obj = ObjectId(CUSTOMER_ID)
    
    customer_entries = get_all_customers()
    for entry in customer_entries:
        if (
            entry["_id"] != str(customer_id_obj)  
            and entry["CUSTOMER_DATA"]["EMAIL"]["VALUE"] == CUSTOMER_DATA["EMAIL"]["VALUE"]
        ):
            return {"MESSAGE": "CUSTOMER EMAIL ALREADY EXISTS."}
        elif (
            entry["_id"] != str(customer_id_obj)  
            and entry["CUSTOMER_DATA"]["MOBILE"]["VALUE"] == CUSTOMER_DATA["MOBILE"]["VALUE"]
        ):
            return {"MESSAGE": "CUSTOMER MOBILE ALREADY EXISTS."}
        elif (
            entry["_id"] != str(customer_id_obj)  
            and entry["CUSTOMER_DATA"]["NAME"]["VALUE"] == CUSTOMER_DATA["NAME"]["VALUE"]
        ):
            return {"MESSAGE": "CUSTOMER NAME ALREADY EXISTS."}

    result = db["Customers"].update_one(
        {"_id": customer_id_obj}, {"$set": {"CUSTOMER_DATA": CUSTOMER_DATA}}
    )
    if result.matched_count == 0:
        return {"MESSAGE": "CUSTOMER NOT FOUND."}
    return {"MESSAGE": "CUSTOMER UPDATED SUCCESSFULLY."}


# Get all customers
def get_all_customers():
    db = get_db()
    entries = list(db["Customers"].find())
    for entry in entries:
        entry["_id"] = str(entry["_id"])
    return entries


# Get a customer by ID
def get_customer_by_id(customer_id):
    db = get_db()
    customer = db["Customers"].find_one({"_id": customer_id})
    if customer is not None:
        customer["_id"] = str(customer["_id"])
    return customer


# Update a customer


# Delete a customer
def DELETE_CUSTOMER(CUSTOMER_ID):
    DB = get_db()
    RESULT = DB["CUSTOMERS"].DELETE_ONE({"_ID": CUSTOMER_ID})
    if RESULT.DELETED_COUNT == 0:
        return {"MESSAGE": "CUSTOMER NOT FOUND."}
    return {"MESSAGE": "CUSTOMER DELETED SUCCESSFULLY."}


if __name__ == "__main__":
    # Test the connection
    if db is not None:
        print("Database connection is active.")
    else:
        print("Database connection is not active.")

    create_customer()
