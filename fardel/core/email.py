import logging

from flask import current_app
from flask_mail import Message

from fardel.ext import mail

from threading import Thread


logger = logging.getLogger(__file__)


def send_async_email(app, msg):
    try:
        with app.app_context():
            mail.send(msg)
    except Exception as err:
        logger.exception("Couldn't send email because of err: %s" % err, exc_info=True)


def send_email(email):
    app = current_app._get_current_object()
    msg = Message(
        subject=email['subject'],
        body=email['text'],
        html=email['html'],
        sender=email['from'],
        recipients=email['to'],
    )
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
