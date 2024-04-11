# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

import subprocess
def send(subject,content):
	msg = EmailMessage()
	msg.set_content(content)
	
	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = subject
	msg['From'] = 'Turtle <qq769711153@hotmail.com>'
	msg['To'] = '769711153@qq.com'
	
	print(msg.as_string())
	
	
	
	subprocess.run(['msmtp', '-t', '769711153@qq.com'], input=msg.as_string().encode())
