from Utility.sms_service import send_sms

status = send_sms(
    "7603800698",
    "SmartAid SMS test successful."
)

print(status)