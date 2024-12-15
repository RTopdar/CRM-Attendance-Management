from flask import Blueprint, request, jsonify
from lib.db import (
    create_customer,
    get_all_customers,
    update_customer_data,
    save_new_customer_data,
    update_client_attendance_entry
)

client_bp = Blueprint("client", __name__)


@client_bp.route("/", methods=["GET"])
def create_new_customer():
    client_form = create_customer()
    return jsonify(
        {
            "MESSAGE": "Ready to create customer entry. Fill in the form.",
            "DATA": client_form,
        },
        200,
    )


@client_bp.route("/all", methods=["GET"])
def get_all_customers_data():
    list = get_all_customers()

    customers = {}

    for customer in list:
        customers[customer["CUSTOMER_DATA"]["NAME"]["VALUE"]] = customer

    return jsonify(
        {"MESSAGE": "All customers retrieved successfully.", "CUSTOMER_DATA": customers}
    )


@client_bp.route("/save", methods=["POST"])
def save_customer_data():
    data = request.json
    CUSTOMER_DATA = data.get("CUSTOMER_DATA")
    response = save_new_customer_data(CUSTOMER_DATA)
    if response["MESSAGE"] == "CUSTOMER DATA SAVED SUCCESSFULLY.":
        return jsonify(response), 200
    else:
        return jsonify(response), 400


@client_bp.route("/update", methods=["PATCH"])
def update_customer():
    data = request.json
    CUSTOMER_ID = data.get("CUSTOMER_ID")
    CUSTOMER_DATA = data.get("CUSTOMER_DATA")

    if CUSTOMER_ID is None:
        return jsonify({"message": "CUSTOMER ID is required."}), 400

    if CUSTOMER_DATA is None:
        return jsonify({"message": "CUSTOMER DATA is required."}), 400

    message = update_customer_data(CUSTOMER_ID, CUSTOMER_DATA)

    if message["MESSAGE"] == "CUSTOMER UPDATED SUCCESSFULLY.":
        return jsonify(message), 200
    else:
        return jsonify(message), 400

@client_bp.route("/bill", methods=["POST"])
def update_customer_billing_data():
    data = request.json
    DATE = data.get("DATE")
    CLIENT_ID = data.get("CLIENT_ID")
    ATTENDANCE_DATA = data.get("ATTENDANCE_DATA")

    if DATE is None:
        return jsonify({"message": "DATE is required."}), 400
    if CLIENT_ID is None:
        return jsonify({"message": "CLIENT_ID is required."}), 400
    if ATTENDANCE_DATA is None:
        return jsonify({"message": "ATTENDANCE_DATA is required."}), 400
    
    message = update_client_attendance_entry(DATE, CLIENT_ID, ATTENDANCE_DATA)

    if message == "Client Attendance Entry Updated Successfully":
        return jsonify({"MESSAGE": message}), 200
    else:
        return jsonify({"MESSAGE": message}), 400