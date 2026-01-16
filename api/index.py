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
BOT_TOKEN = "8456127995:AAGnszGrAjFdkPGRMtDE6yvJmN04wkUNsJE"
ADMIN_ID = "7766821106"
BOT_USERNAME = "imhima_bot"
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

# Helper: Send message to user
def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
        return True
    except Exception as e:
        print(f"Failed to send message to user: {e}")
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
    last_name = data.get('last_name', '')
    username = data.get('username', '')
    referral_code = data.get('referral_code', None)
    chat_id = data.get('chat_id')
    
    full_name = f"{first_name} {last_name}".strip()
    
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    # Send notification to admin with referral info
    msg = (
        f"🚀 *NEW USER STARTED PRIMEADS*\n\n"
        f"👤 *User Details:*\n"
        f"• Name: {full_name}\n"
        f"• Username: @{username if username else 'No Username'}\n"
        f"• User ID: {user_id}\n"
        f"• Chat ID: {chat_id if chat_id else user_id}\n\n"
        f"🎯 *Referral Info:*\n"
        f"• Referral Code Used: {referral_code if referral_code else 'Direct Signup'}\n\n"
        f"📅 *Time:* {current_time}\n"
        f"🤖 *Bot:* @{BOT_USERNAME}"
    )
    
    notify_admin(msg)
    
    # Send welcome message to user if they came via bot
    if referral_code and referral_code != 'undefined' and referral_code != 'null' and referral_code != 'start':
        user_welcome_msg = (
            f"🎉 *Welcome to PrimeAds!*\n\n"
            f"✅ You joined via referral code: *{referral_code}*\n"
            f"💰 *₹10 Bonus* has been added to your account!\n\n"
            f"📊 *Start Earning:*\n"
            f"• Watch ads: ₹0.50 per ad\n"
            f"• Invite friends: ₹10 per referral\n"
            f"• Earn 10% of referrals' earnings\n\n"
            f"💸 *Withdrawal:* Min ₹100 via UPI\n\n"
            f"Need help? Contact @{BOT_USERNAME}"
        )
        if chat_id:
            send_message(chat_id, user_welcome_msg)
    
    return jsonify({
        "status": "success", 
        "message": "User logged in",
        "user_id": user_id,
        "referral_detected": referral_code is not None,
        "bot_username": BOT_USERNAME
    })

# 3. Update Balance Endpoint
@app.route('/api/update_balance', methods=['POST'])
def update_balance():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    user_name = data.get('user_name', 'User')
    type = data.get('type', 'earn')
    
    if user_id and amount:
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        
        msg = (
            f"💰 *BALANCE UPDATE*\n\n"
            f"• User: {user_name}\n"
            f"• User ID: {user_id}\n"
            f"• Amount: ₹{amount}\n"
            f"• Type: {type}\n"
            f"• Time: {current_time}"
        )
        notify_admin(msg)
    
    return jsonify({"status": "success"})

# 4. Referral Bonus Endpoint
@app.route('/api/referral_bonus', methods=['POST'])
def referral_bonus():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name', 'New User')
    referrer_code = data.get('referrer_code')
    bonus_amount = data.get('bonus_amount', 10)
    
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    # Notify admin
    msg = (
        f"🎁 *NEW REFERRAL SUCCESS!*\n\n"
        f"👤 *New User:*\n"
        f"• Name: {user_name}\n"
        f"• User ID: {user_id}\n\n"
        f"👥 *Referral Details:*\n"
        f"• Referred by Code: *{referrer_code}*\n"
        f"• Bonus Amount: ₹{bonus_amount}\n\n"
        f"📅 *Time:* {current_time}\n\n"
        f"✅ *Status:* Bonus credited successfully!"
    )
    notify_admin(msg)
    
    # Try to notify the referrer if we can identify them
    # In a real app, you would look up the referrer's chat_id from database
    # Here we'll just log it
    print(f"Referral: {user_name} ({user_id}) joined via {referrer_code}")
    
    return jsonify({
        "status": "success", 
        "bonus_added": bonus_amount,
        "message": "Referral bonus processed",
        "referrer_notified": False  # Would be True in production with database
    })

# 5. Withdrawal Request Endpoint
@app.route('/api/withdrawal_request', methods=['POST'])
def withdrawal_request():
    data = request.json
    
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    amount = data.get('amount')
    upi_id = data.get('upi_id')
    payment_method = data.get('payment_method')
    referral_code = data.get('referral_code')
    chat_id = data.get('chat_id')
    username = data.get('username', '')
    
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    request_id = f"WDR{int(datetime.now().timestamp())}"
    
    # Send detailed withdrawal request to admin
    admin_msg = (
        f"💸 *WITHDRAWAL REQUEST #{request_id}*\n\n"
        f"👤 *User Details:*\n"
        f"• Name: {user_name}\n"
        f"• Username: @{username if username else 'No Username'}\n"
        f"• User ID: {user_id}\n"
        f"• Chat ID: {chat_id}\n"
        f"• Referral Code: {referral_code}\n\n"
        f"💰 *Payment Details:*\n"
        f"• Amount: ₹{amount}\n"
        f"• UPI ID: `{upi_id}`\n"
        f"• Method: {payment_method}\n\n"
        f"📅 *Time:* {current_time}\n\n"
        f"📝 *ACTION REQUIRED:*\n"
        f"1. Verify user balance\n"
        f"2. Process UPI payment\n"
        f"3. Update status\n\n"
        f"⏰ *Process within 24 hours*\n"
        f"🤖 Contact: @{BOT_USERNAME}"
    )
    
    notify_admin(admin_msg)
    
    # Send confirmation to user
    if chat_id:
        user_msg = (
            f"✅ *Withdrawal Request Submitted!*\n\n"
            f"📋 *Request ID:* #{request_id}\n"
            f"💰 *Amount:* ₹{amount}\n"
            f"📱 *UPI ID:* {upi_id}\n"
            f"💳 *Method:* {payment_method}\n\n"
            f"📊 *Current Status:* Pending Approval\n"
            f"⏰ *Processing Time:* 24 hours\n\n"
            f"📞 *Support:* @{BOT_USERNAME}\n\n"
            f"💡 *Tip:* You can continue earning while waiting!"
        )
        send_message(chat_id, user_msg)
    
    return jsonify({
        "status": "success",
        "message": "Withdrawal request sent to admin",
        "request_id": request_id,
        "estimated_time": "24 hours",
        "bot_username": BOT_USERNAME,
        "timestamp": current_time
    })

# 6. Get Referral Stats
@app.route('/api/referral_stats/<user_id>', methods=['GET'])
def get_referral_stats(user_id):
    # In a real app, fetch from database
    # This is a mock endpoint
    return jsonify({
        "status": "success",
        "user_id": user_id,
        "referrals_count": 0,
        "referral_earnings": 0,
        "referral_code": f"REF{user_id[-6:]}",
        "referral_link": f"https://t.me/{BOT_USERNAME}?start=REF{user_id[-6:]}"
    })

# Vercel Entry Point
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)