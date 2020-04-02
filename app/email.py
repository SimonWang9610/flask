from flask_mail import Message
from flask import render_template
from config import Config
from app import mail
from flask import current_app

def send_email(to, subject, template, **kwargs):
    msg = Message(Config.ITEC_MAIL_SUBJECT_PREFIX + subject,
                  sender=Config.ITEC_MAIL_SENDER, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    # msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)