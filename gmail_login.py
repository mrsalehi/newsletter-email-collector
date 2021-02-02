import smtplib
import imaplib
import email
from time import sleep
import os
from datetime import datetime, date
import yaml
from glob import glob


today = date.today()

GMAIL_USER = 'msreza76@gmail.com'
GMAIL_PASSWORD = 'Salehi76primarypassword'

mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
mail.login(GMAIL_USER, GMAIL_PASSWORD)
mail.list()
mail.select('inbox')

os.makedirs('mails/The Batch', exist_ok=True)
os.makedirs('mails/TechCrunch Week in Review', exist_ok=True)
os.makedirs('mails/TechCrunch Startups Weekly', exist_ok=True)
os.makedirs('mails/The Download MIT', exist_ok=True)


NEWSLETTER_IDENTIFIERS = [  # Tuples of identifier key, value of identifier 
    {
        'From': 'TechCrunch <newsletter@techcrunch.com>', 
        'Subject-prefix': 'Week in Review', 
        'Dest-folder': 'TechCrunch Week in Review'}, 
    {
        'From': 'DeepLearning.AI <thebatch@deeplearning.ai>', 
        'Subject-prefix': 'The Batch', 
        'Dest-folder': 'The Batch'},
    {
        'From': '=?utf-8?Q?The=20Download=20from=20MIT=20Technology=20Review?= <newsletters@technologyreview.com>', 
        'Dest-folder': 'The Download MIT'},
    {
        'From': 'TechCrunch <newsletter@techcrunch.com>',
        'Subject-prefix': 'Startups Weekly',
        'Dest-folder': 'TechCrunch Startups Weekly'}
    ]


while True:
    retcode, mail_ids = mail.search(None, '(UNSEEN)')
    
    for num in mail_ids[0].split():
        typ, data = mail.fetch(num,'(RFC822)')
        
        for response_part in data:
            if isinstance(response_part, tuple):
                original = email.message_from_string(str(response_part[1], 'utf-8'))
                
                subject = original['Subject']

                for identifier in NEWSLETTER_IDENTIFIERS:
                    if identifier['From'] == original['From']:
                        prefix = identifier.get('Subject-prefix', None)
                        if prefix and subject.startswith(prefix):
                            
                            with open(os.path.join('mails', identifier['Dest-folder'], subject + '.eml'), 'w') as fp:
                                fp.write(str(original))
                        elif not prefix:
                            with open(os.path.join('mails', identifier['Dest-folder'], subject + '.eml'), 'w') as fp:
                                fp.write(str(original))

                subject = original['Subject']


                name = subject.replace(' ', '\ ') + '.eml'
                path = f'mails/{name}'

    break
    sleep(60)  # Sleep for a little less than 30 minutes