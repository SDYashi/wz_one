import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com" 
        self.port = 587
        self.username = "mpwz.oneapp@gmail.com"  
        self.password = "nxxgayptypuzfgra"  
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
            print(f"Email sent request completed successfully for {to_email}.")
        except Exception as e:
            print(f"An error occurred while sending email: {str(e)}")
            self.sendemail_disconnect()
            raise

    def send_email_with_cc(self, subject, body, to_email, cc_emails):
        if self.server is None:
            self.sendemail_connect()
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Cc'] = ', '.join(cc_emails)  
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))
            all_recipients = [to_email] + cc_emails
            self.server.sendmail(self.username, all_recipients, msg.as_string())
            print(f"Email sent successfully to {to_email} and CC to {', '.join(cc_emails)}")
        except Exception as e:
            self.sendemail_disconnect()
            raise

    def sendemail_disconnect(self):
        if self.server:
            self.server.quit()

if __name__ == "__main__":
    email_sender = EmailSender()
    email_sender.sendemail_connect()
    # email_sender.send_email("Test Subject", "This is a test email.", "mpwz.oneapp@gmail.com")
    email_sender.send_email_with_cc(
    subject='Meeting Reminder',
    body='Don\'t forget about the meeting tomorrow at 10 AM.',
    to_email='shyam.p8@gmail.com',
    cc_emails=['deepakmarskole88@gmail.com', 'gauravgothi.patidar@gmail.com']
    )    
    email_sender.sendemail_disconnect()