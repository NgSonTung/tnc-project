import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.config.config import JWT_SECRET_KEY, SMTP_SERVER, SMTP_PORT, SMTP_SENDER_MAIL, SMTP_SENDER_PASSWORD


# def send_mail_smtp(receiver_email:str,subject:str,html_content:any):

#         msg = MIMEMultipart()
#         msg['From'] = SMTP_SENDER_MAIL
#         msg['To'] = receiver_email
#         msg['Subject'] = subject
#         html_part = MIMEText(html_content, "html")
#         msg.attach(html_part)
#         context = ssl.create_default_context()

#         with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
#             server.login(SMTP_SENDER_MAIL, SMTP_SENDER_PASSWORD)
#             server.sendmail(SMTP_SENDER_MAIL, receiver_email, msg.as_string())

def send_mail_smtp(receiver_email: str, subject: str, html_content: any):
    msg = MIMEMultipart()
    msg['From'] = SMTP_SENDER_MAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)
    # context = ssl.create_default_context()

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_SENDER_MAIL, SMTP_SENDER_PASSWORD)
        server.sendmail(SMTP_SENDER_MAIL, receiver_email, msg.as_string())
