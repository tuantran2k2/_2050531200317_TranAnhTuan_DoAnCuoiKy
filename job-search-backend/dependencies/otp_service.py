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
    
    
# gửi thông báo khi đã mở khóa user
def send_verification_email_from_admin(user_email):
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from smtplib import SMTP
    
    from_email = _constants.SMTP_USER
    to_email = user_email
    subject = "Email Verification"
    
    # Nội dung HTML của email
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #2E86C1;">Chào mừng!</h2>
        <p>Tài khoản của bạn đã được kích hoạt thành công.</p>
        <p>Bạn có thể đăng nhập và bắt đầu sử dụng các tính năng của chúng tôi ngay bây giờ.</p>
        <p>Nếu bạn cần hỗ trợ, đừng ngần ngại liên hệ với chúng tôi.</p>
        <br>
        <p style="font-size: 0.9em; color: #555;">Trân trọng,</p>
        <p style="font-size: 0.9em; color: #555;">Đội ngũ hỗ trợ</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # Sử dụng định dạng HTML

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