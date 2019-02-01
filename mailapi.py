#!/usr/bin/env python
# coding: utf-8
from flask import Flask, request
from flask_mail import Mail, Message
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.sina.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ''

try:
    import local_settings
    app.config['MAIL_SERVER'] = local_settings.EMAIL_HOST
    app.config['MAIL_PORT'] = local_settings.EMAIL_PORT
    app.config['MAIL_USERNAME'] = local_settings.EMAIL_HOST_USER
    app.config['MAIL_PASSWORD'] = local_settings.EMAIL_HOST_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = 'Lab <'+local_settings.EMAIL_HOST_USER+'>'
except KeyError as e:
    print(e)

mail = Mail(app)


@app.route("/")
def index():
    msg = Message(request.args.get('title'), recipients=[request.args.get('to')])
    msg.body = request.args.get('body')
    msg.html = request.args.get('html')
    mail.send(msg)
    return "Sent"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3434, debug=True)
