from flask import request, make_response
from functools import wraps
import mysql.connector
import re
import os
import uuid

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)


class CustomException(Exception):
    def __init__(self, message, code):
        super().__init__(message)  # Initialize the base class with the message
        self.message = message  # Store additional information (e.g., error code)
        self.code = code  # Store additional information (e.g., error code)

def raise_custom_exception(error, status_code):
    raise CustomException(error, status_code)

##############################
def db():
    db = mysql.connector.connect(
        host="mysql",
        user="root",
        password="password",
        database="company"
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor

###############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view

################################
#def send_verify_email(to_email, user_verification_key):
#    try:
#        # Create a gmail fullflaskdemomail
#        # Enable (turn on) 2 step verification/factor in the google account manager
#        # Visit: https://myaccount.google.com/apppasswords
#
#
#        # Email and password of the sender's Gmail account
#        sender_email = "sebmp48s@gmail.com"
#        password = "YOUR_KEY_HERE"  # If 2FA is on, use an App Password instead
#
#        # Receiver email address
#        receiver_email = "fullflaskdemomail@gmail.com"
#        
#        # Create the email message
#        message = MIMEMultipart()
#        message["From"] = "My company name"
#        message["To"] = receiver_email
#        message["Subject"] = "Please verify your account"
#
#        # Body of the email
#        body = f"""To verify your account, please <a href="http://127.0.0.1/verify/{user_verification_key}">click here</a>"""
#        message.attach(MIMEText(body, "html"))
#
#        # Connect to Gmail's SMTP server and send the email
#        with smtplib.SMTP("smtp.gmail.com", 587) as server:
#            server.starttls()  # Upgrade the connection to secure
#            server.login(sender_email, password)
#            server.sendmail(sender_email, receiver_email, message.as_string())
#        print("Email sent successfully!")
#
#        return "email sent"
#       
#    except Exception as ex:
#        raise_custom_exception("cannot send email", 500)
#    finally:
#        pass
