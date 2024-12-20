import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com" 
        self.port = 587
        self.username = "deepakmarskole88@gmail.com"  
        self.password = "mvakoxppzkinfxkb"  
        self.server = None

    def sendemail_connect(self):
        if self.server is None:
            self.server = smtplib.SMTP(self.smtp_server, self.port)
            self.server.starttls()  
            self.server.login(self.username, self.password)

    def send_email(self, subject, body, to_email):
        if self.server is None:
            self.sendemail_connect()

        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            self.server.sendmail(self.username, to_email, msg.as_string())
        except Exception as e:
            self.sendemail_disconnect()
            raise

    def sendemail_disconnect(self):
        if self.server:
            self.server.quit()


# if __name__ == "__main__":
#     email_sender = EmailSender()
#     email_sender.sendemail_connect()
#     email_sender.send_email("Testing Subject for send email", "This is a test body.", "deepakmarskole88@gmail.com")
#     email_sender.sendemail_disconnect()