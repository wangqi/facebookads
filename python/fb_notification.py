import sys, os, traceback
import smtplib, time
from email.mime.text import MIMEText
import fb_config

"""
    Integrate with multiple notification methods
"""
class FBNotify:

    instance = None

    def __init__(self):
        if FBNotify.instance is None:
            config = fb_config.FBConfig().config
            if ( config.has_section('Email')):
                self.sender = config.get('Email', 'email_sender')
                self.receiver = config.get('Email', 'email_receiver').split(',')
                self.smtpserver = config.get('Email', 'email_smtpserver')
                self.smtpport = config.get('Email', 'email_port')
                self.username = config.get('Email', 'email_username')
                self.password = config.get('Email', 'email_password')
                print("smtpserver:", self.smtpserver)
                print("smtpport:", self.smtpport)
                print("sender:", self.sender)
                print("receiver:", self.receiver)
            FBNotify.instance = self

    """
        Send notification by email
        You have to specify 'Email' section in config file
            email_sender = sender@mail.com
            #email_receiver = user1@mail.com,user2@mail.com
            email_receiver = user1@mail.com
            email_smtpserver = smtp.mail.com
            email_username = user@mail.com
            email_password = password
            email_port = 465
    """
    def notifyByEmail(self, subject, content):
        html = content
        try:
            msg = MIMEText(html, 'html', 'utf-8')
            msg['Subject'] = subject
            smtp = smtplib.SMTP_SSL(self.smtpserver, self.smtpport)
            smtp.connect(self.smtpserver)
            smtp.login(self.username, self.password)
            smtp.sendmail(self.sender, self.receiver, msg.as_string())
            smtp.quit()
        except Exception as err:
            traceback.print_tb(err)

if __name__ == '__main__':
    notify = FBNotify()
    notify.notifyByEmail('Test email', 'Test content')
