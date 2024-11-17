# auth.py
from flask import Blueprint, request, jsonify
from lib.db import create_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("USERNAME")
    email = data.get("EMAIL")
    password = data.get("PASSWORD")

    if not username or not email or not password:
        return jsonify({"message": "Username, email, and password are required."}), 400

    result = create_user(username, email, password)
    return jsonify(result)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("USERNAME")
    password = data.get("PASSWORD")

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    result = login_user(username, password)
    if result["message"] == "Login successful.":
        return jsonify(result)
    else:
        return jsonify(result), 401
