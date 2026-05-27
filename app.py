from fastapi import FastAPI, File, UploadFile
import requests
import os
from datetime import datetime

app = FastAPI()

# ========== TELEGRAM SETTINGS ==========
# These come from Render's environment variables (SECURE)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_photo(image_bytes, caption="🚨 Alert from your security camera!"):
    """Send a photo to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    files = {"photo": ("alert.jpg", image_bytes, "image/jpeg")}
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Telegram photo response: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending photo: {e}")
        return False

def send_telegram_message(message):
    """Send a text message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    try:
        response = requests.post(url, data=data)
        print(f"Telegram message response: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

@app.get("/")
def home():
    return {
        "message": "ESP32 Alert API is working", 
        "status": "online",
        "telegram_configured": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    }

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    """
    ESP32-CAM sends image here when motion/face detected
    """
    # Read the image
    image_bytes = await file.read()
    
    # Send to Telegram
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = f"🚨 PERSON DETECTED!\nTime: {time_now}"
    
    telegram_sent = send_telegram_photo(image_bytes, caption)
    
    return {
        "status": "success",
        "message": "Image received",
        "telegram_sent": telegram_sent,
        "time": time_now
    }

@app.get("/test-telegram")
def test_telegram():
    """Test endpoint to verify Telegram works"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            "error": "Telegram not configured. Add environment variables in Render dashboard.",
            "bot_token_set": bool(TELEGRAM_BOT_TOKEN),
            "chat_id_set": bool(TELEGRAM_CHAT_ID)
        }
    
    success = send_telegram_message("✅ Your ESP32 Alert API is working! This is a test message.")
    
    return {
        "telegram_test": "sent" if success else "failed",
        "bot_token_prefix": TELEGRAM_BOT_TOKEN[:10] + "..." if TELEGRAM_BOT_TOKEN else None,
        "chat_id": TELEGRAM_CHAT_ID
    }

@app.get("/status")
def status():
    """Check system status"""
    return {
        "api_status": "online",
        "telegram_ready": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        "timestamp": datetime.now().isoformat()
    }
