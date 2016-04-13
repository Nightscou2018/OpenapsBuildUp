# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import TwilioRestClient
 
# Find these values at https://twilio.com/user/account
account_sid = "AC7ea2bb7b7476ce5cbc788246fa4edf01"
auth_token = "a423ddc530d5eb395d0bd7c21c8d4f0a"
client = TwilioRestClient(account_sid, auth_token)
 
message = client.messages.create(to="+12069484838", from_="+12062070377",
                                     body="Hello there!")