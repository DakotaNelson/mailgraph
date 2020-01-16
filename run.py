import re
from dateutil import parser as dateParser
import mailbox
import networkx as nx

# you can add time zones here as "time zone code": seconds offset from UTC
tzinfos = {"CDT": -18000}

inbox = mailbox.mbox('data/Inbox.mbox')
G = nx.MultiDiGraph()

inbox.lock() # don't want anyone messing with it while we parse

print("[*] Parsing mailbox now, this can take a while...")

try:
    for message in inbox.itervalues():
        msgFrom = message['from']
        msgTo = message['to']

        if message['date'] is not None:
            msgDate = dateParser.parse(message['date'], tzinfos=tzinfos)
            msgDate = msgDate.isoformat()
        else:
            msgDate = ""

        msgSubject = message['subject']
        if msgSubject is None:
            msgSubject = "(none)"

        # now add it to the graph
        G.add_node(msgFrom)
        G.add_node(msgTo)
        G.add_edge(msgFrom, msgTo, datetime=msgDate, subject=msgSubject)

    print("[*] Writing out GEXF file...")
    nx.write_gexf(G, 'graph.gexf')
finally:
    inbox.close()
