import os
import smtplib
from email.mime.text import MIMEText


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_otp_email(to_email: str, otp: str):

    subject = "1-1Chat OTP"
    body = f"OTP: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = os.environ["EMAIL_ADDRESS"]
    msg["To"] = to_email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()

    server.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
    server.sendmail(os.environ["EMAIL_ADDRESS"], to_email, msg.as_string())

    server.quit()