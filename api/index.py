import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8456127995:AAGnszGrAjFdkPGRMtDE6yvJmN04wkUNsJE")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7766821106"))

# Helper: Send Message to Admin
def notify_admin(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to notify admin: {e}")

# 1. Serve the HTML file
@app.route('/')
def home():
    return send_from_directory('../', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../', path)

# 2. Auth Endpoint (Receives data from JS)
@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    
    # Validate basic data
    if not data or 'id' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    
    user_id = data['id']
    first_name = data.get('first_name', 'User')
    username = data.get('username', 'No Username')
    
    # TODO: Here you should save the user to a database (SQLite, MongoDB, etc.)
    # For now, we just notify the admin
    msg = (
        f"🔔 <b>New User Login!</b>\n"
        f"👤 Name: {first_name}\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"🔗 Username: @{username}"
    )
    notify_admin(msg)
    
    return jsonify({"status": "success", "message": "User logged in"})

# 3. Update Balance Endpoint (Optional)
@app.route('/api/update_balance', methods=['POST'])
def update_balance():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    
    # TODO: Update database balance here
    print(f"User {user_id} earned {amount}")
    
    return jsonify({"status": "success"})

# Vercel Entry Point
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(debug=True)