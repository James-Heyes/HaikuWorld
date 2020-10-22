import sendgrid
import os
from sendgrid.helpers.mail import *
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
SENDGRID_USERNAME = os.environ.get('SENDGRID_USERNAME')
SENDGRID_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
from_email = Email(SENDGRID_USERNAME, name="HaikuWorld")


def sendEmail(to_email, html, subject="default"):
    to_email = To(to_email)
    html = HtmlContent(html)
    mail = Mail(from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html)
    try:
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as exception:
        print(exception)
        return exception


def alertEmail():
    subject = "Out of approved tweets!"
    html = ['''HaikuWorld has run out of approved tweets!\n
                Go to [link] to approve more tweets!''']
    sendEmail(ADMIN_EMAIL, html, subject)
