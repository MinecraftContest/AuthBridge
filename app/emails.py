from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os


def get_smtp():
    server = smtplib.SMTP_SSL(host=os.environ.get('SMTP_HOST'), port=os.environ.get('SMTP_PORT'), )
    server.login(os.environ.get('SMTP_USER'), os.environ.get('SMTP_PASSWORD'))
    return server

def send_email(smtp, email, subject, content):
    msg = MIMEMultipart()

    msg['From'] = os.environ.get('SMTP_USER')
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(content, 'html'))

    smtp.sendmail(msg['From'], email, msg.as_string())