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
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.port)
            self.server.starttls()  
            self.server.login(self.username, self.password)
            print("Connected to the SMTP server.")
        except Exception as e:
            print(f"Failed to connect to the SMTP server: {e}")

    def send_email(self, subject, body, to_email):
        if self.server is None:
            print("You need to connect to the server first.")
            return

        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            self.server.sendmail(self.username, to_email, msg.as_string())
            print(f"Email sent to {to_email}.")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def sendemail_disconnect(self):
        if self.server:
            self.server.quit()
            print("Disconnected from the SMTP server.")


# if __name__ == "__main__":
#     email_sender = EmailSender()
#     email_sender.sendemail_connect()
#     email_sender.send_email("Testing Subject for send email", "This is a test body.", "deepakmarskole88@gmail.com")
#     email_sender.sendemail_disconnect()