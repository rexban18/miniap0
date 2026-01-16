import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# ========== IMPORTANT: USE YOUR EXISTING CREDENTIALS ==========
BOT_TOKEN = "8456127995:AAGnszGrAjFdkPGRMtDE6yvJmN04wkUNsJE"  # Your bot token
ADMIN_ID = "7766821106"  # Your admin ID
# ===============================================================

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
        return True
    except Exception as e:
        print(f"Failed to notify admin: {e}")
        return False

# 1. Serve the HTML file
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# 2. Auth Endpoint - When user starts bot/app
@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    
    if not data or 'id' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    
    user_id = data['id']
    first_name = data.get('first_name', 'User')
    username = data.get('username', 'No Username')
    
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    # Send immediate notification to admin
    msg = (
        f"🚀 *NEW USER STARTED*\n\n"
        f"• Name: {first_name}\n"
        f"• ID: {user_id}\n"
        f"• Username: @{username}\n"
        f"• Time: {current_time}\n"
        f"• App: EWin Big"
    )
    
    notify_admin(msg)
    
    return jsonify({
        "status": "success", 
        "message": "User logged in",
        "user_id": user_id
    })

# 3. Update Balance Endpoint
@app.route('/api/update_balance', methods=['POST'])
def update_balance():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    
    if user_id and amount:
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        
        msg = (
            f"💰 *BALANCE UPDATE*\n\n"
            f"• User ID: {user_id}\n"
            f"• Amount: {amount}\n"
            f"• Time: {current_time}"
        )
        notify_admin(msg)
    
    return jsonify({"status": "success"})

# Vercel Entry Point
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)