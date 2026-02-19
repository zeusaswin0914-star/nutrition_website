"""
Quick test to debug EmailJS API call.
Run: python test_emailjs.py
"""
import requests
import json

EMAILJS_SERVICE_ID = "service_j6rf18v"
EMAILJS_TEMPLATE_ID = "template_3o6dt0k"
EMAILJS_PUBLIC_KEY = "w_RUWZweX4zaKBxGD"
EMAILJS_PRIVATE_KEY = "O_Xc5RzBPpdeNjfC48SyG"
EMAILJS_API_URL = "https://api.emailjs.com/api/v1.0/email/send"

# Test recipient
TEST_EMAIL = "harikrishnaarun5@gmail.com"
TEST_OTP = "123456"

payload = {
    "service_id": EMAILJS_SERVICE_ID,
    "template_id": EMAILJS_TEMPLATE_ID,
    "user_id": EMAILJS_PUBLIC_KEY,
    "accessToken": EMAILJS_PRIVATE_KEY,
    "template_params": {
        "reply_to": TEST_EMAIL,
        "passcode": TEST_OTP,
        "time": "5 minutes"
    }
}

print("=" * 50)
print("EmailJS Debug Test")
print("=" * 50)
print(f"Service ID : {EMAILJS_SERVICE_ID}")
print(f"Template ID: {EMAILJS_TEMPLATE_ID}")
print(f"Public Key : {EMAILJS_PUBLIC_KEY}")
print(f"Sending to : {TEST_EMAIL}")
print("=" * 50)

try:
    response = requests.post(
        EMAILJS_API_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=15
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response   : {response.text}")
    
    if response.status_code == 200:
        print("\nSUCCESS - Email should arrive shortly! Check your inbox.")
    else:
        print(f"\nFAILED - Status {response.status_code}")
        print(f"Error details: {response.text}")
        
except Exception as e:
    print(f"\nEXCEPTION: {e}")
