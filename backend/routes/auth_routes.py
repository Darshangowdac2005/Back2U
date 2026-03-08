# backend/routes/auth_routes.py
import os
import random
import mysql.connector
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from config.db_connector import db
from utils.security import hash_password, verify_password, encode_auth_token
from utils.notification import send_email

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name, email, password, role = data.get('name'), data.get('email'), data.get('password'), data.get('role', 'student')
    if not all([name, email, password]):
        return jsonify({"error": "Missing fields"}), 400

    password_hash = hash_password(password)
    cursor = db.get_cursor()

    try:
        query = "INSERT INTO Users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, password_hash, role))
        db.conn.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": f"Email might exist. {err}"}), 409
    finally:
        cursor.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email, password = data.get('email'), data.get('password')
    cursor = db.get_cursor(dictionary=True)
    cursor.execute("SELECT user_id, password_hash, role FROM Users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if user and verify_password(password, user['password_hash']):
        token = encode_auth_token(user['user_id'], user['role'])
        return jsonify({"message": "Login successful", "token": token, "role": user['role'], "user_id": user['user_id']}), 200

    return jsonify({"error": "Invalid email or password"}), 401


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({"error": "Email is required"}), 400

    cursor = db.get_cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            # Return the same message for security — don't reveal whether email exists
            return jsonify({"message": "If that email is registered, an OTP has been sent."}), 200

        otp = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        # Upsert: delete existing token for this email, then insert new one
        cursor.execute("DELETE FROM password_reset_tokens WHERE email = %s", (email,))
        cursor.execute(
            "INSERT INTO password_reset_tokens (email, otp, expires_at) VALUES (%s, %s, %s)",
            (email, otp, expires_at)
        )
        db.conn.commit()

        subject = "Back2U Password Reset OTP"
        body = (
            f"Hello,\n\n"
            f"You requested a password reset for your Back2U account.\n\n"
            f"Your OTP is: {otp}\n\n"
            f"This OTP is valid for 15 minutes. If you did not request this, please ignore this email.\n\n"
            f"— The Back2U Team"
        )
        send_email(email, subject, body)

        return jsonify({"message": "If that email is registered, an OTP has been sent."}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {e}"}), 500
    finally:
        cursor.close()


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = (data.get('email') or '').strip().lower()
    otp = (data.get('otp') or '').strip()
    new_password = data.get('new_password') or ''

    if not all([email, otp, new_password]):
        return jsonify({"error": "Email, OTP, and new password are required"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    cursor = db.get_cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT otp, expires_at FROM password_reset_tokens WHERE email = %s",
            (email,)
        )
        record = cursor.fetchone()

        if not record:
            return jsonify({"error": "No OTP found for this email. Please request a new one."}), 400

        if record['otp'] != otp:
            return jsonify({"error": "Invalid OTP. Please try again."}), 400

        if datetime.utcnow() > record['expires_at']:
            cursor.execute("DELETE FROM password_reset_tokens WHERE email = %s", (email,))
            db.conn.commit()
            return jsonify({"error": "OTP has expired. Please request a new one."}), 400

        # OTP is valid — update password
        new_hash = hash_password(new_password)
        cursor.execute(
            "UPDATE Users SET password_hash = %s WHERE email = %s",
            (new_hash, email)
        )
        cursor.execute("DELETE FROM password_reset_tokens WHERE email = %s", (email,))
        db.conn.commit()

        return jsonify({"message": "Password reset successful! You can now log in."}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {e}"}), 500
    finally:
        cursor.close()
