# import smtplib
# import email.utils
# import database_connection
# import os
# from models import Users
# from email.mime.text import MIMEText
#
# fromaddr = os.environ.get('MAILER_USERNAME')
# password = os.environ.get('MAILER_PASSWORD')
# server = smtplib.SMTP('smtp.gmail.com', 587)
# server.starttls()
# server.login(fromaddr, password)
#
def send_email(product):
    pass
#     user = Users.objects(username=product.username).first()
#     toaddr = [user.email]
#
#     msg = MIMEText('You have got mail.')
#     msg['To'] = email.utils.formataddr(('Recipient', ','.join(toaddr)))
#     msg['From'] = email.utils.formataddr(('Author', fromaddr))
#     msg['Subject'] = 'Prices dropped !'
#
#     try:
#         server.sendmail(fromaddr, toaddr, msg.as_string())
#     except:
#         pass
#
