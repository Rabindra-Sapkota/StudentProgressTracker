from mailerpy import Mailer
import os


def send_progress_email(to_email, mail_subject, mail_body):
    mail_password = os.environ.get("EMAIL_PASSWORD")
    if not mail_password:
        raise ValueError("EMAIL_PASSWORD not set in environment")

    mailer = Mailer("smtp.gmail.com", 587, "rabindrasapkota2@gmail.com", mail_password)
    mailer.send_mail(to_email, mail_subject, mail_body)
