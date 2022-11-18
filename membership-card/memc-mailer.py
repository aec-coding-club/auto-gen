#!/usr/bin/env python

"""
memc-mailer.py: Script to mass-mail membership cards
  - output source directory labelled `out` in script's root (output dump of gen-cards.py)
  - sub dirs formatted as 'out/{UID}%{EMAIL}'
  - memc items labelled ['out/{UID}%{email}/1.png', 'out/{UID}%{email}/2.png']
"""

import os, smtplib, time
from email.message import EmailMessage

__author__ = "Jayanta Pandit"
__version__ = "1.0.0"
__email__ = "jay.dnb@outlook.in"
__license__ = "GPL"
__date__ = "Nov 19, 2022"

SMTP_EMAIL = '__________@gmail.com'
SMTP_LOGIN_PWD = '___________'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_SERVER_PORT = 587

def send_memc(s: smtplib.SMTP, email: str, side1_p: str, side2_p: str):
    # Create the container email message.
    msg = EmailMessage()
    msg['Subject'] = 'AECCC Membership Card (Soft Copy)'
    msg['From'] = f'AECCC Coding Club <{SMTP_EMAIL}>'
    msg['To'] = email.lower()

    # Set the plain-text body.
    msg.set_content(
        """
Hi!

Your AECCC UID has been generated, along with the promised soft-copy of the AECCC membership card.
Find them in the attachments.

Regards,
Team AECCC
        """
    )

    # Open the files in binary mode. You can also omit the subtype
    # if you want MIMEImage to guess it.
    for file in [side1_p, side2_p]:
        with open(file, 'rb') as fp:
            img_data = fp.read()
            msg.add_attachment(
                img_data, 
                maintype='image', 
                subtype='png', 
                filename=f'aeccc.{email}.{file.split(os.sep)[-1]}'
            )
            fp.close()

    # Send mail with attachments.
    s.send_message(msg)

if __name__ == '__main__':
    dirs = os.listdir(os.path.join(os.getcwd(), 'out'))
    smtp_inst = smtplib.SMTP(SMTP_SERVER)
    print('\x1b[1m')
    print(f'[ \x1b[34;1m  Log  \x1b[39m ] Init TLS handshake...', flush=True)
    smtp_inst.starttls()
    print(f'[ \x1b[34;1m  Log  \x1b[39m ] Logging in...', flush=True)
    smtp_inst.login(SMTP_EMAIL, SMTP_LOGIN_PWD)
    print()
    
    for i in dirs:
        uid, recipient = i.split('%')
        prettier_uid = f'{uid:<20}'
        print(f'[ \x1b[33;1mSending\x1b[39m ] {prettier_uid} ➜ {recipient}', end='', flush=True)
        try:
            send_memc(
                smtp_inst,
                i.split('%')[1],
                os.path.join(os.getcwd(), 'out', i, '1.png'),
                os.path.join(os.getcwd(), 'out', i, '2.png')
            )
            print(f'\r[  \x1b[32;1mSent ✓\x1b[39m ] {prettier_uid} ➜ {recipient}', flush=True)
            time.sleep(0.3)
        except Exception as e:
            print(f'\r[  \x1b[31mError \x1b[39m ] {prettier_uid} ➜ {recipient}', flush=True)

    print('\x1b[0m')
    smtp_inst.quit()
