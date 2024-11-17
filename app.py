# app.py
from crypt import methods
from email import message
from flask import Flask, request, jsonify, Response
from lib.db import (
    get_db,
)
from lib.auth import auth_bp
from lib.workers import worker_bp
from lib.client import client_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(worker_bp, url_prefix="/workers")
app.register_blueprint(client_bp, url_prefix="/clients")

import os
from dotenv import load_dotenv

load_dotenv()

VERSION = os.environ.get("VERSION", "v0.0.1")


@app.route("/")
def home():
    db = get_db()
    if db is not None:
        return {
            "MESSAGE": "Human Resource Management System API.",
            "VERSION": VERSION,
        }
    return "Unable to connect to MongoDB"


if __name__ == "__main__":
    import os

    PORT = os.environ.get("PORT", 8080)
    app.run(debug=True, host="0.0.0.0", port=PORT)
