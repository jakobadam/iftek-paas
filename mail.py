import smtplib
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Header import Header

from app import app

EMAIL_FROM = app.config.get('EMAIL_FROM') 
EMAIL_SERVER = app.config.get('EMAIL_SERVER')
EMAIL_ADMINS = app.config.get('ADMINS')

def encode_header(header):
    return str(Header(unicode(header), 'utf-8'))

def send(sender=EMAIL_FROM, receivers=None, subject='', text='', html=''):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = encode_header(subject)
        msg['From'] = encode_header(EMAIL_FROM)
        receivers = [encode_header(r) for r in receivers]
        msg['To'] = ' ,'.join(receivers)
        
        part1 = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
        part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
        
        if text:
            msg.attach(part1)
        if html:
            msg.attach(part2)
        
        server = smtplib.SMTP(EMAIL_SERVER)
        if app.config['MODE'] != 'test':
            server.sendmail(sender, receivers, msg.as_string())
            logging.info('mail: sending mail %s to %s from %s' % (msg['Subject'], msg['From'], msg['To']))
        else:
            logging.info('mail: skipping sending mail %s to %s from %s' % (msg['Subject'], msg['From'], msg['To']))
        server.quit()
    except Exception, e:
        logging.error('mail error: %s' % e)

def send_admin(subject='', text='', html=''):
    send(receivers=EMAIL_ADMINS, subject=subject, text=text, html=html)

    
