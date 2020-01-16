import re
from dateutil import parser as dateParser
import mailbox

inbox = mailbox.mbox('data/Inbox.mbox')

inbox.lock() # don't want anyone messing with it while we parse

print("[*] Parsing mailbox now, this can take a while...")

try:
    for message in inbox.itervalues():
        msgData = {
                "from": message['from'],
                "to": message['to'],
                "date": dateParser.parse(message['date'])
                }
        print(msgData)
except:
    inbox.close()
    raise
