""" 
Written for Python 2.7.x
Requires mechanize library 
	
"""

from mechanize import Browser
br = Browser()
url = ''

from sys import stdout
from time import sleep
import urllib
import re
import getpass
from datetime import datetime, date, time
from agent import agent
from ticket import ticket

        
def proccessComments(my_ticket, my_agentList):

    for item in my_ticket.comments:
        for e in my_agentList:
            if e.name == item:
                #print "Adding to an existing agent!"
                e.totalComments += 1
                return


        #print "Creating new agent!"
        new_agent = agent(item, 0, 0, 0, 0, 0, 0)
        my_agentList.append(new_agent)
        my_agentList[len(my_agentList) - 1].totalComments += 1
        return


def proccessEmails(my_ticket, my_agentList):
    for item in my_ticket.emails:
        if not re.findall('.@.', item):
            for e in my_agentList:
                if e.name == item:
                    #print "Adding to an existing agent!"
                    e.totalEmails += 1
                    return

            #print "Creating new agent!"
            new_agent = agent(item, 0, 0, 0, 0, 0, 0)
            my_agentList.append(new_agent)
            my_agentList[len(my_agentList) - 1].totalEmails += 1
            return

def proccessSubject(my_ticket, my_agentList):

    if re.findall(".Phone.", my_ticket.subject):
        for e in my_agentList:
            if e.name == my_ticket.owner:
                #print "Adding to an existing agent!"
                e.totalPhone += 1
                return True

        # We didn't find a match in the agent list.
        #print "Creating new agent!"
        new_agent = agent(my_ticket.owner, 0, 0, 0, 0, 0, 0)
        my_agentList.append(new_agent)
        my_agentList[len(my_agentList) - 1].totalPhone += 1

        return True

    elif re.findall(".Walk-in.", my_ticket.subject):
        for e in my_agentList:
            if e.name == my_ticket.owner:
                #print "Adding to an existing agent!"
                e.totalWalkin += 1
                return True

        # We didn't find a match in the agent list.
        #print "Creating new agent!"
        new_agent = agent(my_ticket.owner, 0, 0, 0, 0, 0, 0)
        my_agentList.append(new_agent)
        my_agentList[len(my_agentList) - 1].totalWalkin += 1

        return True

    else:
        return False



def proccessCreatedBy(my_ticket, my_agentList):

    # If we find an @ in the string it must be a user email address.
    for item in my_ticket.createdBy:
        if not re.findall('.@.', item):
            for e in my_agentList:
                if e.name == item:
                    #print "Adding to an existing agent!"
                    e.ticketsCreated += 1
                    return

            # We didn't find a match in the agent list.
            #print "Creating new agent!"
            new_agent = agent(item, 0, 0, 0, 0, 0, 0)
            my_agentList.append(new_agent)
            my_agentList[len(my_agentList) - 1].ticketsCreated += 1
            return
    

def proccessResolvedBy(my_ticket, my_agentList):

    for item in my_ticket.resolvedBy:
        for e in my_agentList:
            if e.name == item:
                #print "Adding to an existing agent!"
                e.ticketsResolved += 1
                return


        #print "Creating new agent!"
        new_agent = agent(item, 0, 0, 0, 0, 0, 0)
        my_agentList.append(new_agent)
        my_agentList[len(my_agentList) - 1].ticketsResolved += 1
        return

        
def getSearchList(ticketList, the_query):

     
    q1 = "search/ticket?query="

    #For some reason RT expects ONLY the query portion to be RFC 1738 encoded.
    q2 = urllib.quote(the_query)


    #print url + q1 + q2
    response = br.open(url + q1 + q2)

    # the following can be added after the query to authenticate
    # would work well without SSO in the way.
    # u = "user=my_username"
    # p = "pass=my_password"
    # + "&"  + u + "&" + p)

    page = response.read()

    #print page

    matches = []
    
    matches = re.findall('^\d{1,12}: ', page, flags=re.M)

    #Add our findings to the ticketList  
    for s in matches:
        ticketList.append(s.strip(": "))

    return page


def proccessList(ticketList, currentTicket, agentList, the_query):

    num = 0
    total_hours = 0
    avg_hours = 0

    print('\n' + "Query: " + the_query)

    for item in ticketList:
        print "\rProcessing record: ",num,
        stdout.flush()
        sleep(1)
                        
        #print 'Processing record', num
        currentTicket.proccessTicket(item, br, url)
        total_hours = total_hours + currentTicket.timeOpen

        proccessEmails(currentTicket, agentList)
        proccessComments(currentTicket, agentList)
        
        if not proccessSubject(currentTicket, agentList):
            proccessCreatedBy(currentTicket, agentList)
            proccessResolvedBy(currentTicket, agentList)

        num += 1

    stdout.write("\n") # move the cursor to the next line

    if num is not 0:
        avg_hours = total_hours / num

    f = open('queryresults.csv', 'a')
    f.write("Query: " + the_query + '\n')
    f.write('Username,Created,Resolved,Comments,Emails,Phone,Walkin \n')

    for e in agentList:
        f.write(e.name + ',' + str(e.ticketsCreated) + ',' + str(e.ticketsResolved) + ',' + str(e.totalComments) + ',' + str(e.totalEmails) + ',' + str(e.totalPhone) + ',' + str(e.totalWalkin) + '\n') 

    f.write("Total tickets in query: " + str(num) + '\n')
    f.write("Average hours a ticket was open: " + "%.2f" % avg_hours + "\n \n")
    f.close()

def importFiles(my_queryList):

    global url
    global br

    with open('RTserver.txt', 'r') as f:
        content = f.readline()

    f.close()
    
    url = content

    f = open('querylist.txt', 'r')

        

    with open('querylist.txt', 'r') as f:
        my_queryList = f.readlines()

    f.close()

    my_user = ''
    my_pass = ''

    while my_user == '':
        my_user = raw_input('Username: ')
        if my_user == '':
            print "Blank username please try again."

    while my_pass == '':
        my_pass = getpass.getpass('Password: ')
        if my_pass == '':
            print "Blank password please try again."
    

    #Set our mechanize variables.
    br.set_handle_robots( False )
    br.addheaders = [('User-agent', 'Firefox')]

    #Authorize yourself on PDX SSO
    br.open("https://sso.pdx.edu")
    br.select_form(nr=0)
    br['username'] = my_user
    br['password'] = my_pass
    br.submit()

    return my_queryList



queryList = []
ticketList = []
agentList = []
currentTicket = ticket()

queryList = importFiles(queryList)

for item in queryList:
    my_query = item
    currentPage = getSearchList(ticketList, my_query)
    proccessList(ticketList, currentTicket, agentList, my_query)

print("\nDone!\n")


# Below are examples of query syntax and useful test queries.
#my_query = "Status = 'open' AND Queue = 'uss-labs-idsc'"

#my_query = "id = 399958"

#200 tickets
#my_query = "Status = 'resolved' AND Created > '2014-03-21' AND Queue = 'uss-helpdesk'"

#600 tickets
#my_query = "Status = 'resolved' AND Created > '2014-03-14' AND Queue = 'uss-helpdesk'"

#1500 tickets
#my_query = "Status = 'resolved' AND Created > '2014-03-01' AND Queue = 'uss-helpdesk'"

# Proccess the ticketList to be searched and create
# a copy of the current page results
#currentPage = getSearchList(ticketList, my_query)

#proccessList(ticketList, currentTicket, agentList)




""" Random code snippets for later reference. 
response = br.open('https://stage.support.oit.pdx.edu')

print "Let's print the html code that was returned!"
print response.code
print response.read()

for link in br.links():
    print link

"""

#Print information about one queue
#/REST/1.0/queue/ofsa-requests
#response = br.open('https://stage.support.oit.pdx.edu/REST/1.0/queue/ofsa-requests')
#print response.read()

#Print all tickets from one queue, uses query.
#/REST/1.0/search/ticket?query=Queue='fooQueue'
#response = br.open('https://stage.support.oit.pdx.edu/REST/1.0/search/ticket?query=Queue="'"ofsa-requests"'"')
#print response.read()

#Print a single ticket HISTORY
#/REST/1.0/ticket/<ticket-id>/history
# response = br.open('https://stage.support.oit.pdx.edu/REST/1.0/ticket/115048/history')
# print(response.read())

# Get ticket properties not including comments or histor.
# /REST/1.0/ticket/<ticket-id>/show
# response = br.open('https://stage.support.oit.pdx.edu/REST/1.0/ticket/115048/show')
# print response.read()

"""

# Save to a file.
fileobj = open('ticket.txt', 'a')
fileobj.write(response.read())
fileobj.close()



textfile = open('ticket.txt', 'r')
filetext = textfile.read()
textfile.close()

"""

"""
response = br.open('https://stage.support.oit.pdx.edu/REST/1.0/search/ticket?query=Queue="'"ofsa-requests"'"')
matches = re.findall("\d{1,6}:", response.read())

modify_matches = []

for s in matches:
    modify_matches.append(s.strip(':'))

print(modify_matches)
"""



    
# print([s.strip(':') for s in matches]) # remove the 8 from the string borders
# print([s.replace(':', '') for s in matches]) # remove all the 8s
"""
fileobj = open('results.txt', 'a')

print([s.strip(':') for s in matches]) >> fileobj, item

fileobj.close()
"""
