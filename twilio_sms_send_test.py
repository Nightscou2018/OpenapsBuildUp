#!/usr/bin/python3
"""
Script tries to obtain current reservoir level and battery voltage.
If either is below a set threshold (based on date and time), an SMS is sent.
A sent notification file is created so that SMS's are only sent every so often if the warning is being ignored.
"""

from datetime import datetime
from datetime import time
import json
import subprocess

VOLTAGE_THRESHOLD = 1.36
SCHOOLNIGHT_TIME_THRESHOLD = time(20,0)  #(hour(24), minute)
RESERVOIR_WARN = 30
RESERVOIR_URGENT = 15
NOTIFICATION_ELASPED_TIME_HOURS = 4
textfileTESTING = True
timedateTESTING = True

if textfileTESTING == False:
    try:  # open the reservoir level file
        with open('monitor/reservoir.json') as data_file:    
            reservoir_level = json.load(data_file)
    except:
        print ("error loading monitor/battery.json")
else:
    reservoir_level = 15

if timedateTESTING == False:
    # Figure out time and day of the week right NOW (http://stackoverflow.com/questions/415511/how-to-get-current-time-in-python, 
    # http://stackoverflow.com/questions/1831410/python-time-comparison)
    now = datetime.now()
    now_time = now.time()
    print("now_time =",now_time)
    print(type(now_time))
    weekday = now.weekday()  # Get day of the week of Now (Return the day of the week as an integer, where Monday is 0 and Sunday is 6.)
else:
    weekday = 4

# If it's (past 8pm the night before a work day and the reservoir is < 30 units) or (the reservoir is < 15 units)
if (weekday >= 0 and weekday < 4) or (weekday == 6):  # School nights
    if now_time >= time(SCHOOLNIGHT_TIME_THRESHOLD):
        if reservoir_level <= RESERVOIR_WARN:  # send the SMS
            print('yep-res_warn')
        else:
            print('nope-res_warn')
    else:
        print('nope-time')
else:
    print('nope-weekday')

if reservoir_level <= RESERVOIR_URGENT: # send the SMS
    print('yep-res_urg')

if reservoir_level > RESERVOIR_WARN + 20:  # remove the sent file
    try:
        output = subprocess.Popen(["rm", "-f", "Scripts/sent-reservoir-sms"], stdout=subprocess.PIPE).communicate()[0]
    except:
        print ('error deleting sent reservoir SMS file')


def check_for_sms_sent_file(NOTIFICATION_ELASPED_TIME_HOURS,reservoir_level):
    try:  # if there is a reservoir sent notification file present
        last_touched_in_secs_since_epoch = subprocess.Popen(["stat", "-c", "%Y","Scripts/sent-reservoir-sms"], stdout=subprocess.PIPE).communicate()[0]
        now_in_secs_since_epoch = subprocess.Popen(["printf '%(%s)T\n' -1"], stdout=subprocess.PIPE).communicate()[0]
        elapsed_secs = now_in_secs_since_epoch - last_touched_in_secs_since_epoch
        
        # if so, see how much time has elapsed since last SMS sent
        if elapsed_secs >= (NOTIFICATION_ELASPED_TIME_HOURS*3600):
            # send another SMS and update the reservoir sent notification file
            send_reservoir_sms(reservoir_level)
            update_reservoir_sent_file
        else
            print('not enough time has elapsed')
    except:
        # send an SMS and create/update the reservoir sent notification file
        send_reservoir_sms(reservoir_level)
        update_reservoir_sent_file

def send_reservoir_sms(reservoir_level):
    try:
        # Download the twilio-python library from http://twilio.com/docs/libraries 
        from twilio.rest import TwilioRestClient
        # Find these values at https://twilio.com/user/account
        account_sid = "AC7ea2bb7b7476ce5cbc788246fa4edf01"
        auth_token = "a423ddc530d5eb395d0bd7c21c8d4f0a"
        client = TwilioRestClient(account_sid, auth_token)

        message_body = "reservoir = "+str(reservoir_level)+" units"
        message = client.messages.create(to="+12069484838", from_="+12062070377", body=message_body)

        print('reservoir SMS sent')
    except:
        print ('error sending reservoir SMS')

def update_reservoir_sent_file():
    try:
        output = subprocess.Popen(["touch","Scripts/sent-reservoir-sms"], stdout=subprocess.PIPE).communicate()[0]
        print('sent file updated')
    except:
        print('error updating reservoir sent file')

'''
# Try to grab battery voltage 
try:  # open the reservoir level file
    with open('monitor/battery.json') as data_file:    
        battery_level = json.load(data_file)
    voltage = battery_level["voltage"]
except:
    print ("error loading monitor/battery.json")
'''

# If the battery voltage is less than 1.28 Volts ??
    # if there is a battery sent notification file present
        # if so, see how much time has elapsed since last SMS sent
            # if it's been more than YY hours
                # send another SMS and update the battery sent notification file
            # else
                # done
    # else
        # send an SMS and create/update the battery sent notification file  