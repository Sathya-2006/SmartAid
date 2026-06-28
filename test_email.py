from Utility.email_service import send_email

status = send_email(
    "yourpersonalemail@gmail.com",
    "SmartAid Test",
    "Email notification working successfully."
)

print(status)