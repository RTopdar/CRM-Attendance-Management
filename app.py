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
from lib.auth import auth_bp
from lib.workers import worker_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(worker_bp, url_prefix='/workers')

import os
from dotenv import load_dotenv
load_dotenv()

VERSION = os.environ.get("VERSION", "v0.0.1")




@app.route("/")
def home():
    db = get_db()
    if db is not None:
        return f"Attendance Management System API v{VERSION}"
    return "Unable to connect to MongoDB"




if __name__ == "__main__":
    import os
    PORT = os.environ.get("PORT", 8080)
    app.run(debug=True, host="0.0.0.0", port=PORT)
