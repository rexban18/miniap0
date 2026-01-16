import os
import json
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

# --- YEH SABSE ZAROORI HAI ---
# Yeh line allow karti hai ki app (Frontend) backend se baat kare
CORS(app, resources={r"/*": {"origins": "*"}}) 

# --- CONFIGURATION ---
# Token aur ID yahan set kiye gaye hain (Environment variables prefer karein production mein)
BOT_TOKEN = os.environ.get("8456127995:AAGnszGrAjFdkPGRMtDE6yvJmN04wkUNsJE", "8456127995:AAGnszGrAjFdkPGRMtDE6yvJmN04wkUNsJE")
ADMIN_ID = os.environ.get("7766821106", "7766821106")

def send_telegram_message(text):
    """Function jo directly Admin ko message bhejta hai"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        # Timeout 10 second rakha hai taaki app hang na ho
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# --- ROUTES ---

# 1. Serve HTML File (Jab user app kholega)
@app.route('/')
def home():
    return send_from_directory('../', 'index.html')

# 2. Static Files Serve Karne ke liye (Images, CSS, etc)
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../', path)

# 3. Notify Admin on Login (Jab user login kare)
@app.route('/api/login_notify', methods=['POST'])
def login_notify():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        message = data.get('message', 'User logged in')
        send_telegram_message(message)
        
        return jsonify({"status": "success", "message": "Login notified"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# 4. Notify Admin of Referral (Jab koi refer kare)
@app.route('/api/referral', methods=['POST'])
def referral():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        message = data.get('message', 'New referral')
        send_telegram_message(message)
        
        return jsonify({"status": "success", "message": "Referral notified"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# 5. Notify Admin of Withdrawal Request (Jab user withdraw manga)
@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        message = data.get('message', 'Withdrawal request')
        send_telegram_message(message)
        
        return jsonify({"status": "success", "message": "Withdrawal notified"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# --- VERCEL HANDLER ---
# Yeh function Vercel ko batata hai ki yeh Python server run karna hai
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    # Local testing ke liye debug=True rakha hai
    app.run(debug=True, port=5000)