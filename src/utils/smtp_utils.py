import smtplib
from email.mime.text import MIMEText
from email.header import Header
import base64

mail_host = 'smtp.live.com'
from_addr = 'jasonlift@outlook.com'
passwd_b = b'IUQ0OTIwOTEyMDQ='
passwd = base64.b64decode(passwd_b).decode()

subject = 'IrOnPrem Alarm'
msg = """
    Dear Master, 

    This is an offline message for ir-sensors %s. 
    FYI.

    Yours Truly,
    OnPrem Robot
    """

"""
sensor_info is a list of dict
for example: [{'id1': 'name1', 'id2': 'name2'}]
"""
def send_emails(sensor_info, receivers):
    try:
        server = smtplib.SMTP('smtp.live.com', 25)
        server.connect("smtp.live.com", 587)
        server.ehlo()
        server.starttls()
        server.login(from_addr, passwd)
        message = MIMEText(msg % str(sensor_info), 'plain', 'utf-8')
        message['From'] = from_addr
        if isinstance(receivers, str):
            receivers = [receivers]
        message['To'] = ','.join(receivers)
        message['Subject'] = Header(subject, 'utf-8')
        server.sendmail(from_addr, receivers, message.as_string())
        server.quit()
        return 200, "ok"
    except Exception as e:
        return 500, repr(e)
