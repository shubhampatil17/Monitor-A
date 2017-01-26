import smtplib
import email.utils
from email.mime.text import MIMEText

msg = MIMEText('You have got mail.')
msg['To'] = email.utils.formataddr(('Recipient', 'shubhteenax17@gmail.com'))
msg['From'] = email.utils.formataddr(('Author', 'abc@monitora.com'))
msg['Subject'] = 'Prices dropped !'

server = smtplib.SMTP('127.0.0.1', 5001)
server.set_debuglevel(True)

try:
    server.sendmail('abc@monitora.com', ['shubhteenax17@gmail.com'], msg.as_string())
finally:
    server.quit()