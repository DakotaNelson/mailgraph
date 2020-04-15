import re
import argparse
from dateutil import parser as dateParser
import datetime
import mailbox
import networkx as nx

parser = argparse.ArgumentParser(description='Parse mbox files into graph \
        files readable by Gephi or other graph analysis tools.')

parser.add_argument('--output-file', '-o', default='graph.gexf')
parser.add_argument('input_files', nargs='+')
# TODO include a flag to pseudonynomize the output

# you can add time zones here as "time zone code": seconds offset from UTC
tzinfos = {"CDT": -18000}

args = parser.parse_args()

def parseAddress(s):
    # given a string that is the value of a to: or from: field,
    # parse out all unique email addresses and attempt to make
    # them canonical... sort of... somehow
    # returns a list of 1 or more recipients

    # finds instances of "Doe, John" <jdoe@example.com>
    # they mess up the comma-separation when we split the addresses
    quotedName = re.compile('".+?(,).+?"')

    # if s is none, tag it as a string else things get weird
    if s is None:
        s = "(unknown)"

    # lowercase everything to prevent capitalization-based duplicates
    s = s.lower()
    # remove commas in quoted blocks - e.g. "Doe, John" <jdoe@example.com>
    s = re.sub(quotedName, '', s)
    # if the comma is in the form email1@example.com, email2@example.com, then
    # we need to split it up so that each email gets its own list element
    if ',' in s:
        s = s.strip().split(',')
        s = [st.strip() for st in s]
    else:
        # regardless, we need it to be a list now (even if only 1 element)
        s = [s]

    outVal = []
    # if in the format "John Doe <jdoe@example.com>" extract just the part
    # between the brackets
    bracketField = re.compile("\<(.*)\>")
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

# the "mode" thing is just a static attribute on the graph that Gephi looks for
# to be able to have graphs that change over time (... are dynamic)
G = nx.MultiDiGraph(mode="dynamic")

inboxes = args.input_files
for toProcess in inboxes:
    print("[*] Opening {} for processing.".format(toProcess))
    # TODO: put something here to check that 'toProcess' exists?
    # right now if it doesn't exist it almost-silently skips
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

            # NOTE this is a semi-important default!
            defaultTime = datetime.datetime.now() - datetime.timedelta(days=365*5)
            # I do not care about leap years, it's fine

            if message['date'] is not None:
                msgDate = dateParser.parse(message['date'], tzinfos=tzinfos)
            else:
                msgDate = defaultTime
            msgDateISO = msgDate.isoformat()

            # this seems to make Gephi unhappy for some reason
            # msgSubject = message['subject']
            # if msgSubject is None:
            #     msgSubject = "(none)"

            for recipient in msgTo:
                for sender in msgFrom:
                    G.add_edge(
                        sender,
                        recipient,
                        datetime=msgDateISO,
                        start=msgDate.timestamp(),
                        mode="dynamic"
                    )
    finally:
        inbox.close()

print("[*] Writing out GEXF file...")
nx.write_gexf(G, args.output_file, prettyprint=False)
print("[*] Done writing {}".format(args.output_file))
