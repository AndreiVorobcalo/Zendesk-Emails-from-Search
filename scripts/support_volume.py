# support_volume.py
# This script is designed to be run once an hour
# it searches for the given tags over a specified
# time period. For each result, the requester email
# is extracted and appended to a spreadsheet

import configparser
import logging
import smtplib
import os
import pandas as pd
import json
import TicketCounter as TC


config = configparser.RawConfigParser()
config.read('../src/auth.ini')
OUTPUT_FILE = config['default']['EmailList'].strip('"')
DOMAIN = config['zendesk']['Domain'].strip('"')
AUTH = config['zendesk']['Credentials'].strip('"')
SENDER = config['email']['Sender'].strip('"')
PASS = config['email']['Password'].strip('"')
RECIPIENT = config['email']['Recipient'].strip('"')
TAGS = config['mods']['SearchTags']

def main(logger, filename, domain, auth):

    # Initialize an empty list to hold the emails
    EmailList = []

    logger.warning('Checking if Output File exists...')
    if not os.path.exists(OUTPUT_FILE):
        logger.warning('Output File not found. Creating...')
        #import in csv as list
        columns = list(range(24))
        EmailList = pd.DataFrame(columns = columns)
        EmailList.to_csv(filename)
        logger.warning('Output File generated and ready for usage.')
    else:
        logger.warning('Output File already exists. Querying new results.')

    #st0, st1, xdst0, xtst0, xtst1 = TC.get_formatted_datetimes(1)

   
    # need tag(s), start & end time (defaults past hour)
    TicketResults = TC.get_tickets(DOMAIN, AUTH, TAGS)
    for ticket in TicketResults['results']:
        EmailList.append(ticket['via']['source']['from']['address'])
    try:
        # save email list to csv
        lst = TC.get_formatted_datetimes(1)
        lst = json.loads(lst.text)
        EmailList.to_csv(filename)
        pass 
    except Exception as e:
        logger.warning('Error saving file, {}'.format(str(e)))

    try:
        logger.warning("Sending report to {}\n".format(RECIPIENT))
        #send_report(RECIPIENT, TicketCountVar, tags, delta, (SENDER, PASS))
    except Exception as e:
        logger.exception('{}\nError sending the report!'.format(str(e)))
    logger.warning('SUCCESS')



# takes the recipient email, hourly count, and frequent tags as arguments
# auth should be a tuple containing the sender email id and sender email id password
# builds a message and sends it to the recipient

def send_report(to, count, tags, delta, auth = None, subject='Email List Update!'):
    try:
        # creates SMTP session
        email = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        email.starttls()

        # authentication
        email.login(auth[0], auth[1])

        # craft the message
        message = ("Greetings Crunchyroll Humans, ")#.format(count, delta, tags)
        message = 'Subject: {}\n\n{}'.format(subject, message).encode('utf-8')

        # send the email
        email.sendmail(auth[0], to, message)

        # terminate the session
        email.quit()
    except Exception as e:
        print('ERROR: ', str(e))
        exit()
    return 0




if __name__ =="__main__":
    # TODO: set logging level based on input
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    main(logger)