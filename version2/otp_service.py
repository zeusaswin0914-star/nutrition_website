import random
import string
import logging
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_otp(length=6):
    """Generate a random numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


# EmailJS Configuration
# Get these from your EmailJS dashboard: https://dashboard.emailjs.com/admin
EMAILJS_SERVICE_ID = "service_j6rf18v"    # Gmail service
EMAILJS_TEMPLATE_ID = "template_3o6dt0k"  # One-Time Password template
EMAILJS_PUBLIC_KEY = "w_RUWZweX4zaKBxGD"
EMAILJS_PRIVATE_KEY = "O_Xc5RzBPpdeNjfC48SyG"

# EmailJS API endpoint
EMAILJS_API_URL = "https://api.emailjs.com/api/v1.0/email/send"

def send_otp_email(receiver_email, otp):
    """
    Sends an OTP email using EmailJS REST API.
    Falls back to terminal logging if the request fails.
    """
    # Always log to terminal for Development/Fallback
    print("\n" + "="*40)
    print(f" [OTP SERVICE] To: {receiver_email}")
    print(f" [OTP SERVICE] Code: {otp}")
    print("="*40 + "\n")
    logger.info(f"OTP generated for {receiver_email}: {otp}")

    # Prepare EmailJS payload
    # Template variables match the EmailJS "One-Time Password" template
    # Template "To Email" field uses {{reply_to}} so the recipient email must be sent as "reply_to"
    # Template body uses {{passcode}} for the OTP and {{time}} for validity
    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,
        "accessToken": EMAILJS_PRIVATE_KEY,
        "template_params": {
            "reply_to": receiver_email,   # Maps to {{reply_to}} in "To Email" field
            "passcode": otp,              # Maps to {{passcode}} in template body
            "time": "5 minutes"           # Maps to {{time}} in template body
        }
    }

    # Try sending via EmailJS
    try:
        response = requests.post(
            EMAILJS_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f" [OTP SERVICE] Email sent successfully via EmailJS to {receiver_email}")
            logger.info(f"EmailJS email sent to {receiver_email}")
            return True
        else:
            print(f" [OTP WARNING] EmailJS returned status {response.status_code}: {response.text}")
            logger.warning(f"EmailJS failed with status {response.status_code}")
            # Still return True so flow continues (using the printed code for dev)
            return True
        
    except Exception as e:
        print(f" [OTP ERROR] Failed to send email via EmailJS: {e}")
        logger.error(f"EmailJS error: {e}")
        # Return True anyway so flow continues (using the printed code)
        return True
