import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def send_sms(phone, message):
    try:
        if not ACCOUNT_SID or not AUTH_TOKEN or not FROM_NUMBER:
            print("Twilio credentials missing.")
            return False

        phone = str(phone).strip()

        if phone.startswith("0"):
            phone = "+91" + phone[1:]
        elif not phone.startswith("+"):
            phone = "+91" + phone

        client = Client(ACCOUNT_SID, AUTH_TOKEN)

        client.messages.create(
            body=message,
            from_=FROM_NUMBER,
            to=phone
        )

        return True

    except Exception as e:
        print("SMS Error:", e)
        return False