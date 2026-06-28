import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_email(receiver_email, subject, message):
    """
    Send email using Gmail SMTP
    Returns True if successful, False otherwise
    """

    try:

        msg = MIMEMultipart()

        msg["From"] = EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(
            MIMEText(message, "plain")
        )

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            EMAIL,
            APP_PASSWORD
        )

        server.sendmail(
            EMAIL,
            receiver_email,
            msg.as_string()
        )

        server.quit()

        return True

    except Exception as e:
        print("Email Error:", e)
        return False