import smtplib
import imaplib
import email
from time import sleep
import os
from datetime import datetime
import yaml
from glob import glob
import calendar
from numpy.random import permutation

GMAIL_USER = 'msreza76@gmail.com'
GMAIL_PASSWORD = 'Salehi76primarypassword'
GMAIL = imaplib.IMAP4_SSL('imap.gmail.com', 993)
GMAIL.login(GMAIL_USER, GMAIL_PASSWORD)
GMAIL.list()
GMAIL.select('inbox')


NEWSLETTER_IDENTIFIERS = [  # Tuples of identifier key, value of identifier 
    {
        'From': 'TechCrunch <newsletter@techcrunch.com>', 
        'Subject-prefix': 'Week in Review', 
        'Dest-folder': 'TechCrunch Week in Review'}, 
    {
        'From': '"DeepLearning.AI" <thebatch@deeplearning.ai>', 
        'Subject-prefix': 'The Batch', 
        'Dest-folder': 'The Batch'},
    {
        'From': '=?utf-8?Q?The=20Download=20from=20MIT=20Technology=20Review?= <newsletters@technologyreview.com>', 
        'Dest-folder': 'The Download MIT'},
    {
        'From': 'TechCrunch <newsletter@techcrunch.com>',
        'Subject-prefix': 'Startups Weekly',
        'Dest-folder': 'TechCrunch Startups Weekly'},
    {
        'From': '"Artificial Intelligence Weekly" <hello@faveeo.com>',
        'Subject-prefix': 'AI News Weekly',
        'Dest-folder': 'AI News Weekly'},
    {
        'From': "=?utf-8?Q?Deep=20Learning=20Weekly?= <deeplearningweekly@gmail.com>",
        'Dest-folder': 'Deep Learning Weekly'}
    ]

for identifier in NEWSLETTER_IDENTIFIERS:
    os.makedirs(f"/Users/mrezasalehi/email-assistant/mails/{identifier['Dest-folder']}", exist_ok=True)


def format_name(subj):
    subj = subj.replace(' ', '\ ')
    subj = subj.replace('$', '\$')

    return subj

def get_current_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def get_yaml_list():
    if os.path.exists('/Users/mrezasalehi/email-assistant/mail_list.yaml'):
        with open('/Users/mrezasalehi/email-assistant/mail_list.yaml') as fptr:
            return yaml.load(fptr, Loader=yaml.FullLoader)
    
    yaml_list = {
        'The Batch': [], 
        'TechCrunch Startups Weekly': [], 
        'TechCrunch Week in Review': [],
        'The Download MIT': [],
        'AI News Weekly': [],
        'Deep Learning Weekly': []}
    
    save_yaml_list(yaml_list)

    return yaml_list


def save_yaml_list(yaml_list):
    with open('/Users/mrezasalehi/email-assistant/mail_list.yaml', 'w') as fptr:
        yaml.dump(yaml_list, fptr)
    

def mark_as_seen_yaml_list(yaml_list, publisher, id_):
    for el in yaml_list[publisher]:
        if el['id'] == id_:
            el[read] = True
            return
    
    save_yaml_list(yaml_list)


def add_to_yaml_list(yaml_list, publisher, date, subject, read=False):
    id_ = len(yaml_list[publisher]) + 1 

    yaml_list[publisher].append({
        'id': id_,
        'Date': date,
        'Subject': subject,
        'read': read
    })

    save_yaml_list(yaml_list)


def check_for_new_mails():
    retcode, mail_ids = GMAIL.search(None, '(UNSEEN)')
    yaml_list = get_yaml_list()

    mails = []

    for num in mail_ids[0].split():
        ret, mail = GMAIL.fetch(num,'(RFC822)')

        if ret == 'OK':
            data = mail[0]
            if isinstance(data, tuple):
                mails.append(email.message_from_string(str(data[1], 'utf-8')))

    return mails


def suggest_reading(yaml_list):
    publishers = [k for k in yaml_list]

    for publisher in permutation(publishers):
        for email in permutation(yaml_list[publisher]):
            if not email['read']:
                email['read'] = True
                save_yaml_list(yaml_list)
                return publisher, email

    return None, None


def main():
    yaml_list = get_yaml_list()
    mails = check_for_new_mails()

    for mail in mails:
        subject = mail['Subject']
        for identifier in NEWSLETTER_IDENTIFIERS:
            if identifier['From'] == mail['From']:
                prefix = identifier.get('Subject-prefix', None)
                if prefix and subject.startswith(prefix):
                    with open(os.path.join('/Users/mrezasalehi/email-assistant/mails', identifier['Dest-folder'], subject + '.eml'), 'w') as fp:
                        fp.write(str(mail))
                        add_to_yaml_list(
                            yaml_list, 
                            identifier['Dest-folder'],
                            f'{datetime.today().day} {calendar.month_name[datetime.today().month]} {datetime.today().year}',
                            subject)
                
                elif not prefix:
                    with open(os.path.join('/Users/mrezasalehi/email-assistant/mails', identifier['Dest-folder'], subject + '.eml'), 'w') as fp:
                        fp.write(str(mail))
                        add_to_yaml_list(
                            yaml_list, 
                            identifier['Dest-folder'],
                            f'{datetime.today().day} {calendar.month_name[datetime.today().month]} {datetime.today().year}',
                            subject)

    current_time = get_current_time()

    publisher, email = suggest_reading(yaml_list)
    if email is not None:
        path = os.path.join('/Users/mrezasalehi/email-assistant/mails', format_name(publisher), format_name(email['Subject']) + '.eml')
        os.system("open " + path)



if __name__ == '__main__':
    main()