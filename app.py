from fastapi import FastAPI, File, UploadFile
import requests
import os
from datetime import datetime

app = FastAPI()

# ========== TELEGRAM SETTINGS ==========
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_message(message):
    """Send a text message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"success": False, "error": "Missing credentials"}
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    
    try:
        response = requests.post(url, data=data)
        result = response.json()
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_telegram_photo(image_bytes, caption):
    """Send a photo to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"success": False, "error": "Missing credentials"}
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    files = {"photo": ("alert.jpg", image_bytes, "image/jpeg")}
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
    
    try:
        response = requests.post(url, files=files, data=data)
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def home():
    return {
        "message": "ESP32 Alert API is working", 
        "status": "online",
        "telegram_configured": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        "bot_token_preview": TELEGRAM_BOT_TOKEN[:15] + "..." if TELEGRAM_BOT_TOKEN else None,
        "chat_id": TELEGRAM_CHAT_ID
    }

@app.get("/test-telegram")
def test_telegram():
    """Detailed test to debug Telegram issues"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            "error": "Telegram not configured",
            "bot_token_set": bool(TELEGRAM_BOT_TOKEN),
            "chat_id_set": bool(TELEGRAM_CHAT_ID)
        }
    
    # Try to send a test message
    result = send_telegram_message("✅ Test message from your ESP32 Alert API!")
    
    # Also try to get bot info to verify token is valid
    bot_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        bot_info = requests.get(bot_url).json()
    except:
        bot_info = {"error": "Could not fetch bot info"}
    
    return {
        "message_sent": result,
        "bot_info": bot_info,
        "your_chat_id": TELEGRAM_CHAT_ID,
        "help": "Make sure you have started a chat with your bot first"
    }

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    """ESP32-CAM sends image here"""
    image_bytes = await file.read()
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = f"🚨 PERSON DETECTED!\nTime: {time_now}"
    
    result = send_telegram_photo(image_bytes, caption)
    
    return {
        "status": "success",
        "telegram_sent": result.get("success", False),
        "telegram_response": result,
        "time": time_now
    }

@app.get("/status")
def status():
    return {
        "api_status": "online",
        "telegram_ready": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        "timestamp": datetime.now().isoformat()
    }
