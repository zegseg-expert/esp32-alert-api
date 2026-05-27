from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
def home():
    return {"message": "ESP32 Alert API is working", "status": "online"}

@app.get("/detect")
def detect():
    return {"message": "Detection endpoint ready", "alert": "false"}

@app.post("/detect")
def detect_post():
    return {"message": "Image received", "alert": "true", "telegram_sent": True}
