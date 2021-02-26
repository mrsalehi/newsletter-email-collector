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
from decouple import config

GMAIL_USER = config('GMAIL_USER')
GMAIL_PASSWORD = config('GMAIL_PASSWORD')

GMAIL = imaplib.IMAP4_SSL('imap.gmail.com', 993)
GMAIL.login(GMAIL_USER, GMAIL_PASSWORD)
GMAIL.list()
GMAIL.select('inbox')


with open('/Users/mrezasalehi/email-assistant/newsletter-providers.yaml', 'r') as fptr:
    NEWSLETTER_IDENTIFIERS = yaml.load(fptr, Loader=yaml.FullLoader)

for identifier in NEWSLETTER_IDENTIFIERS:
    os.makedirs(f"/Users/mrezasalehi/email-assistant/mails/{identifier['Dest-folder']}", exist_ok=True)


def format_name(subj):
    subj = subj.replace(' ', '\ ')
    subj = subj.replace('$', '\$')

    return subj


def format_date(date_str):
    day, month, year = date_str.split()

    return day + '-' + month[:3] + '-' + year


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
        date = '-'.join(mail['Date'].split()[1:4])

        if date.startswith('0'):
            date = date[1:]

        for identifier in NEWSLETTER_IDENTIFIERS:
            if identifier['From'] == mail['From']:
                prefix = identifier.get('Subject-prefix', None)
                if prefix and subject.startswith(prefix):
                    with open(os.path.join('/Users/mrezasalehi/email-assistant/mails', identifier['Dest-folder'], date + '.eml'), 'w') as fp:
                        fp.write(str(mail))
                        add_to_yaml_list(
                            yaml_list, 
                            identifier['Dest-folder'],
                            f'{datetime.today().day} {calendar.month_name[datetime.today().month]} {datetime.today().year}',
                            subject)
                
                elif not prefix:
                    with open(os.path.join('/Users/mrezasalehi/email-assistant/mails', identifier['Dest-folder'], date + '.eml'), 'w') as fp:
                        fp.write(str(mail))
                        add_to_yaml_list(
                            yaml_list, 
                            identifier['Dest-folder'],
                            f'{datetime.today().day} {calendar.month_name[datetime.today().month]} {datetime.today().year}',
                            subject)

    current_time = get_current_time()

    publisher, email = suggest_reading(yaml_list)
    if email is not None:
        path = os.path.join('/Users/mrezasalehi/email-assistant/mails', format_name(publisher), format_date(email['Date']) + '.eml')
        os.system("open " + path)



if __name__ == '__main__':
    main()