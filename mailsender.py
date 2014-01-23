import sys
import smtplib
import threading
from logger import Logger
from email_recipient import EmailRecipient
from server_credentials import ServerCredentials, DecodeString
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


logger = Logger('mailsender')
logger.addLogFile('webdiff.log')


class EmailList:
    def __init__(self):
        self.recipients = []
        self.messages = []


class MailSenderThread(threading.Thread):
    def __init__(self, emails, credentials):
        threading.Thread.__init__(self)
        self.__emails = emails
        self.__credentials = credentials
    
    
    def run(self):
        try:
            server = smtplib.SMTP(host=self.__credentials.smtp_server,
                                  port=self.__credentials.smtp_port,
                                  timeout=30)
            server.set_debuglevel(1)
            server.starttls()
            server.login(self.__credentials.username, DecodeString(self.__credentials.password))
            for i in range(len(self.__emails.messages)):
                logger.debug('[ ] Sending email to '
                             + self.__emails.recipients[i].name
                             + ' (' + self.__emails.recipients[i].address + ')'
                             + '...')
                
                server.sendmail(from_addr = self.__credentials.from_addr,
                                to_addrs = self.__emails.recipients[i].address,
                                msg = self.__emails.messages[i].as_string())
                
                logger.info('[>] Email sent to '
                            + self.__emails.recipients[i].name
                            + ' (' + self.__emails.recipients[i].address + ')'
                            + ' [' + str(i+1) + '/' + str(len(self.__emails.messages)) + ']')
            server.quit()
        
        except Exception, e:
            logger.error('[!] EXCEPTION: ' + str(e))
        sys.exit()



class MailSender:
    
    def __init__(self, server_credentials):
        self.credentials = server_credentials
    
    
    def send(self, message, email_recipients=[]):
        emails = EmailList()
        for recipient in email_recipients:
            emails.recipients.append(recipient)
            emails.messages.append(self.__build_message(message, recipient))
            
        mailer = MailSenderThread(emails, self.credentials)
        mailer.start()

    
    def __build_message(self, message, recipient):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[Webdiff] Change detected'
        msg['From'] = self.credentials.from_addr
        msg['To'] = recipient.name + ' <' + recipient.address + '>'
        msg['Reply-to'] = 'no-reply@pieroland.net'
        
        html = message

        html_part = MIMEText(html, 'html')
        msg.attach(html_part)

        return msg


    def __messageToHtml(self, message):
        html = []
        text = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '&para;<br>')
        html.append(text)
        return ''.join(html)
