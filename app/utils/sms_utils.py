# FILE: app/utils/sms_utils.py

import requests
from os import getenv
from dotenv import load_dotenv

load_dotenv()

AT_USERNAME = getenv("AFRICASTALKING_USERNAME")
AT_API_KEY = getenv("AFRICASTALKING_API_KEY")
AT_SENDER_ID = getenv("AFRICASTALKING_SENDER_ID", "20414")  # fallback if not in .env
AT_BASE_URL = "https://api.africastalking.com/version1/messaging"

def send_sms(phone_number: str, message: str, bulk_sms_mode: int = 1) -> dict:
    headers = {
        "apiKey": AT_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "username": AT_USERNAME,
        "to": phone_number,
        "message": message,
        "from": AT_SENDER_ID,
        "bulkSMSMode": bulk_sms_mode
    }

    try:
        response = requests.post(AT_BASE_URL, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Error sending SMS:", e)
        return {"error": str(e)}
