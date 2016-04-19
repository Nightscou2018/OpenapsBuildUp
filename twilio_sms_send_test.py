#!/usr/bin/python2

"""
Script tries to obtain current reservoir level and battery voltage.
If either is below a set threshold (based on date and time), an SMS is sent.
A sent notification file is created so that SMS's are only sent every so often if the warning is being ignored.
"""


#------------------------------------------------------------------------------------------------------
# Twilio SMS hello world

# Download the twilio-python library from http://twilio.com/docs/libraries 
from twilio.rest import TwilioRestClient
 
# Find these values at https://twilio.com/user/account
account_sid = "AC7ea2bb7b7476ce5cbc788246fa4edf01"
auth_token = "a423ddc530d5eb395d0bd7c21c8d4f0a"

client = TwilioRestClient(account_sid, auth_token) 
message = client.messages.create(to="+12069484838", from_="+12062070377", body="Hello there!")

print ("SMS sent")

#------------------------------------------------------------------------------------------------------
# example read/write JSON file (from enact.py)

import json
import subprocess

try:  # open the enact/suggest file
    with open('enact/suggested.json') as data_file:    
        suggested_data = json.load(data_file)
except:
    print ("error loading enact/suggested.json")

try:  # parse the enact/suggested file and see if there is a duration in there
    duration = suggested_data['duration']
    rate = suggested_data['rate']
    temp = suggested_data['temp']
    
    try:  # write a temp file that will be used to enact a new temp basal
        with open('enact/temp.json', 'w') as file:
            temp_json = ({"duration":duration,"rate":rate,"temp":temp})
            file.write = json.dump(temp_json,file,indent=2,separators=(',', ':'),sort_keys=True)
            
    except:
        print ("error writing out enact/temp.json file")



#------------------------------------------------------------------------------------------------------
# Pseudocode for reservoir status SMS

# Try to grab reservoir level
# Figure out time and day of the week right NOW
# If it's (past 8pm the night before a work day and the reservoir is < 30 units) or (the reservoir is < 15 units)
    # if there is a reservoir sent notification file present
        # if so, see how much time has elapsed since last SMS sent
            # if it's been more than YY hours
                # send another SMS and update the reservoir sent notification file
            # else
                # done
    # else
        # send an SMS and create/update the reservoir sent notification file

# Try to grab battery voltage 
# If the battery voltage is less than 1.28 Volts ??
    # if there is a battery sent notification file present
        # if so, see how much time has elapsed since last SMS sent
            # if it's been more than YY hours
                # send another SMS and update the battery sent notification file
            # else
                # done
    # else
        # send an SMS and create/update the battery sent notification file  



#------------------------------------------------------------------------------------------------------
# Write the code HERE:

import datetime

# Get day of the week of Now (Return the day of the week as an integer, where Monday is 0 and Sunday is 6.)
time_now = datetime.datetime.today()
day_of_the_week = time_now.weekday()

# http://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
# http://stackoverflow.com/questions/1831410/python-time-comparison