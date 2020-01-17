import re
from dateutil import parser as dateParser
import mailbox
import networkx as nx

# you can add time zones here as "time zone code": seconds offset from UTC
tzinfos = {"CDT": -18000}

def parseAddress(s):
    # given a string that is the value of a to: or from: field,
    # parse out all unique email addresses and attempt to make
    # them canonical... sort of... somehow
    # returns a list of 1 or more recipients

    # finds instances of "Doe, John" <jdoe@example.com>
    # they mess up the comma-separation when we split the addresses
    quotedName = re.compile('".+?(,).+?"')

    # if in the format "John Doe <jdoe@example.com>" extract just the part
    # between the brackets
    bracketField = re.compile("\<(.*)\>")

    # if s is none, tag it as a string else things get weird
    if s is None:
        s = "(unknown)"

    s = s.lower()
    # remove commas in quoted blocks - e.g. "Doe, John" <jdoe@example.com>
    s = re.sub(quotedName, '', s)
    # if it's in the form email1@example.com, email2@example.com, then
    # we need to split it up so that each email gets its own list element
    if ',' in s:
        s = s.strip().split(',')
        s = [st.strip() for st in s]
    else:
        # regardless, we need it to be a list now (even if only 1 element)
        s = [s]

    outVal = []
    for element in s:
        # pull any emails in brackets out - so e.g. the next two lines should
        # come out to be equivalent:
        # "Jane Doe" <jdoe@example.com>
        # jdoe@example.com
        # ... and the best way I can find to do that is pull just the email
        # address out of the brackets
        regMatch = bracketField.search(element)
        if regMatch is not None:
            outVal.append(regMatch.group(1))
        else:
            outVal.append(element)

    return outVal

G = nx.MultiDiGraph()
inboxes = ['data/Inbox.mbox']
for toProcess in inboxes:
    print("[*] Opening {} for processing.".format(toProcess))
    inbox = mailbox.mbox(toProcess)

    inbox.lock() # don't want anyone messing with it while we parse

    print("[*] Parsing mailbox, this can take a while.")

    try:
        for index,message in inbox.iteritems():
            # keep the user appraised of our progress
            if index == 0:
                print("[*] Working through messages now...")
            elif index % 10000 == 0:
                print("[*] Processed {} messages.".format(index))

            msgFrom = parseAddress(message['from'])
            msgTo = parseAddress(message['to'])

            if message['date'] is not None:
                msgDate = dateParser.parse(message['date'], tzinfos=tzinfos)
                msgDateISO = msgDate.isoformat()
            else:
                msgDate = ""

            msgSubject = message['subject']
            if msgSubject is None:
                msgSubject = "(none)"

            for recipient in msgTo:
                for sender in msgFrom:
                    G.add_edge(sender, recipient, datetime=msgDateISO, startopen=msgDate.timestamp())
    finally:
        inbox.close()

print("[*] Writing out GEXF file...")
nx.write_gexf(G, 'graph.gexf', prettyprint=False)
