#!/usr/bin/python3
import subprocess
import datetime
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser

# ----------------------------------------------------------------------
#       GLOBAL VARIABLES
# ----------------------------------------------------------------------
log_file=''
last_file=''
last_timestamp=''
last_line=''

path_config = '/sshcontroller/config.ini' # INSERT THE CONFIGURATION FILE PATH

# ----------------------------------------------------------------------
#       FUNCTIONS
# ----------------------------------------------------------------------
def saveLast(last):
    f = open(last_file,"w")
    f.write(last)
    f.close()

def readLast():
    global last_line
    global last_timestamp
    el_time = 'Jan 01 00:00:01'
    try:
        f = open(last_file,"r")
        last_line = f.readline()
        f.close()
    except FileNotFoundError:
        f = open(last_file,"w")
        f.close()

    if( isinstance(last_line,str) and len(last_line) > 1):
        elements = last_line.split(' ')
        el_time = elements[0] + ' ' + elements[1] + ' ' + elements[2]

    last_timestamp = datetime.datetime.strptime(el_time, "%b %d %H:%M:%S")


def send_email(obj,corpo):
    global path_config
    config = configparser.ConfigParser()
    config.read(path_config)
    
    # I read the variables from configuration files
    SMTP_HOST       = config['MAIL']['SMTP_HOST']
    SMTP_PORT       = config['MAIL']['SMTP_PORT']
    USER            = config['MAIL']['USER']
    PASSWORD        = config['MAIL']['PASSWORD']
    SENDER          = config['MAIL']['SENDER']
    RECIPIENT       = config['MAIL']['RECIPIENT']
    NAME_SERVER     = config['MAIL']['NAME_SERVER']

    RECIPIENTS = RECIPIENT.split(',')

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    obj = "[ " + NAME_SERVER + " ] " + obj
    msg['Subject'] =obj
    msg['From'] = SENDER
    msg['To'] = "<" + RECIPIENT.replace(",",">,<") + ">"

    # Create the body of the message (a plain-text and an HTML version).
    text = "[ " + NAME_SERVER + " ] \n" +corpo
    html = "[ " + NAME_SERVER + " ] <br>" +corpo

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP(SMTP_HOST,SMTP_PORT)
    s.starttls()
    s.login(USER,PASSWORD)

    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(SENDER, RECIPIENTS, msg.as_string())
    s.quit()

def main():
    global path_config
    global log_file
    global last_file
    global last_timestamp
    global last_line
    config = configparser.ConfigParser()
    config.read(path_config)
    # I read the variables from configuration files
    log_file    = config['FILE']['log_file']
    last_file   = config['FILE']['last_file']
    time_start = '[ {:%Y-%m-%d %H:%M:%S} ] Server started'.format(datetime.datetime.now())
    obj='SSHCONTROLLER STARTED'
    msg= time_start
    send_email(obj,msg)
    readLast()
    f = subprocess.Popen(['tail','-F',log_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True)
    while True:
        line = f.stdout.readline()
        if( isinstance(line,str) and len(line) > 1):
            line = line.replace('  ',' ')
            elements = line.split(' ')
            el_time = elements[0] + ' ' + elements[1] + ' ' + elements[2]
            timestamp = datetime.datetime.strptime(el_time, "%b %d %H:%M:%S")
            if ("ssh" in line) and (line !=last_line) and (timestamp > last_timestamp):
                obj=''
                msg=''
                if "Accepted" in line:
                    obj='SSH CONNECTION ACCEPTED'
                    msg=line
                    send_email(obj,msg)
                    saveLast(line)
                    readLast()

while(True):
    try:
        main()
    except:
        time.sleep(60)

