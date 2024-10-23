# app.py
from crypt import methods
from email import message
from flask import Flask, request, jsonify, Response
from lib.db import (
    create_Attendance_Entry,
    generate_csv_report,
    get_all_attendance_entries,
    get_all_worker_data,
    get_db,
    update_attendance_entry,
)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    db = get_db()
    if db is not None:
        return "Attendance Management System API v0.0.1"
    return "Unable to connect to MongoDB"


@app.route("/workers", methods=["GET"])
def get_all_workers():
    list = get_all_worker_data()
    return jsonify(list)


@app.route("/workers/all", methods=["GET"])
def get_all_attendance():
    list = get_all_attendance_entries()
    attendance_Data = {}
    for entry in list:
        attendance_Data[entry["DATE"]] = entry
    return jsonify(attendance_Data)


@app.route("/workers/attendance", methods=["GET"])
def get_attendance_entry():
    date = request.args.get("DATE")

    if date is None:
        return jsonify({"message": "Date is required."}), 400

    WORKER_DATA = create_Attendance_Entry(date)

    return jsonify(
        {
            "message": "Attendance Entry Created/Fetched Successfully",
            "WORKER_DATA": WORKER_DATA,
        }
    )


@app.route("/workers/attendance", methods=["POST"])
def save_attendance_entry():
    data = request.json
    date = data.get("DATE")
    WORKER_DATA = data.get("WORKER_DATA")

    if date is None:
        return jsonify({"message": "Date is required."}), 400

    if WORKER_DATA is None:
        return jsonify({"message": "Worker Data is required."}), 400

    message = update_attendance_entry(date, WORKER_DATA)

    return jsonify({"message": message})


@app.route("/workers/attendance/report", methods=["GET"])
def get_attendance_report():
    date = request.args.get("DATE")

    if date is None:
        return jsonify({"message": "Date is required."}), 400

    worker_data = generate_csv_report(date)

    return Response(
        worker_data,
        mimetype="text/csv",
        headers={
            "Content-disposition": f"attachment; filename=Attendance_Report_{date}.csv"
        },
    )


if __name__ == "__main__":
    import os

    PORT = os.environ.get("PORT", 8080)
    app.run(debug=True, host="0.0.0.0", port=PORT)
