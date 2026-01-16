import os
import json
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8456127995:AAGnszGrAjFdkPGRMtDE6yvJmN04wkUNsJE")
ADMIN_ID = os.environ.get("ADMIN_ID", "7766821106")

# --- HELPER FUNCTION ---
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

# --- ROUTES ---

# 1. Serve HTML
@app.route('/')
def home():
    return send_from_directory('../', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../', path)

# 2. Notify Admin on Login
@app.route('/api/login_notify', methods=['POST'])
def login_notify():
    data = request.json
    message = data.get('message', 'User logged in')
    send_telegram_message(message)
    return jsonify({"status": "success"})

# 3. Notify Admin of Referral
@app.route('/api/referral', methods=['POST'])
def referral():
    data = request.json
    message = data.get('message', 'New referral')
    send_telegram_message(message)
    return jsonify({"status": "success"})

# 4. Notify Admin of Withdrawal Request
@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    message = data.get('message', 'Withdrawal request')
    send_telegram_message(message)
    return jsonify({"status": "success"})

# Vercel Handler
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(debug=True)