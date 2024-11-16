from flask import Blueprint, request, jsonify

from lib.db import (
    create_Attendance_Entry,
    generate_csv_report,
    get_all_attendance_entries,
    get_all_worker_data,
    get_db,
    update_attendance_entry,
)

worker_bp = Blueprint("worker", __name__)


@worker_bp.route("/", methods=["GET"])
def get_all_workers():
    list = get_all_worker_data()
    return jsonify(list)


@worker_bp.route("/all", methods=["GET"])
def get_all_attendance():
    list = get_all_attendance_entries()
    attendance_Data = {}
    for entry in list:
        attendance_Data[entry["DATE"]] = entry
    return jsonify(attendance_Data)


@worker_bp.route("/attendance", methods=["GET"])
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


@worker_bp.route("/attendance", methods=["POST"])
def save_attendance_entry():
    data = request.json
    date = data.get("DATE")
    WORKER_DATA = data.get("WORKER_LIST")

    if date is None:
        return jsonify({"message": "Date is required."}), 400

    if WORKER_DATA is None:
        return jsonify({"message": "Worker Data is required."}), 400

    message = update_attendance_entry(date, WORKER_DATA)

    return jsonify({"message": message})


@worker_bp.route("/attendance/report", methods=["GET"])
def get_attendance_report():
    date = request.args.get("DATE")

    if date is None:
        return jsonify({"message": "Date is required."}), 400

    worker_data = generate_csv_report(date)
    return jsonify(worker_data)
