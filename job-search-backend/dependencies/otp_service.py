from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from datetime import datetime, timedelta, timezone

import random
import os
import _constants
import jwt


def generate_otp(user_email):
    verification_code = jwt.encode(
        {
            'user_email': user_email,
            'exp': datetime.utcnow() + timedelta(seconds=_constants.VERIFICATION_TIMEOUT)
        },
        _constants.SECRET_KEY, algorithm='HS256'
    )
    verification_code = str(random.randint(100000, 999999)) 
    return verification_code



# Function to send verification code email
def send_verification_email(user_email, verification_code):
    from_email = _constants.SMTP_USER
    to_email = user_email
    subject = "Email Verification"
    body = f"Your verification code is: {verification_code}"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = SMTP(_constants.SMTP_SERVER, _constants.SMTP_PORT)
        server.starttls()
        server.login(from_email, _constants.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False