import smtplib
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email import Encoders

class Mailer(object):

    def __init__(self, server, user, password,subject, from_email, to_emails, 
                txt_msg = '', html_msg = '', attachments = []):

        self.server = server
        self.user = user
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
        self.txt_msg = txt_msg
        self.html_msg = html_msg

        COMMASPACE = ', '

        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = subject
        # me == the sender's email address
        # family = the list of all recipients' email addresses
        msg['From'] = self.from_email
        msg['To'] = COMMASPACE.join(self.to_emails)
        text = self.txt_msg
        html = """\
        <html>
          <head></head>
          <body>
            %s
          </body>
        </html>
        """ % (self.html_msg)

        body = MIMEMultipart('alternative')
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        body.attach(part1)
        body.attach(part2)
        msg.attach(body)
        for attachment in attachments:
            if attachment['filename'].find('doc') > 0:
                attachFile = MIMEBase('application', 'msword')     
            elif attachment['filename'].find('pdf') > 0:
                attachFile = MIMEBase('application', 'pdf')	
            else:
                attachFile = MIMEBase('application', 'octet-stream')    

            attachFile.set_payload(attachment['data'])

            Encoders.encode_base64(attachFile)
            attachFile.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])

            msg.attach(attachFile)	
		    
        self.msg = msg
        
    def send(self, *args, **kw):
        #s=smtplib.SMTP('smtp.gmail.com:587')
        s=smtplib.SMTP(self.server)
        s.starttls()
        s.login(self.user,self.password)
        s.sendmail(self.from_email, self.to_emails, self.msg.as_string())
        s.close()	    
