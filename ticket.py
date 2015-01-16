from agent import agent
import re

from mechanize import Browser
br = Browser()

url = ''

from datetime import datetime, date, time
import urllib


class ticket(object):
    subject = ""
    num = 0
    owner = ""
    timeOpen = 0
    
    createdBy = []
    resolvedBy = []
    commenents = []
    emails = []
    historyID = []
       
    
    # The class "constructor" - It's actually an initializer 
    def __init__(self):
        self.subject = ""
        self.num = 0
        self.owner = ""
        self.timeOpen = 0
        self.createdBy = []
        self.resolvedBy = []
        self.comments = []
        self.emails = []
        self.historyID = []


    def make_ticket(sujbect, num, owner, createdBy, resolvedBy, timeOpen, comments, emails, historyID):
        ticket = ticket(subject, num, owner, createdBy, resolvedBy, timeOpen, comments, emails, historyID)
        return ticket


    def convert_timedelta(self, duration):
        seconds = duration.total_seconds()
        hours = seconds / 3600
        return hours

    def captureOwner(self, page):
        # Should have only one owner per ticket.
        owner = re.findall("Owner: .*", page)
        modify_owner = ''.join(owner)

        #This should already be the owner we will analyze later.
        modify_owner = re.sub("Owner: ", "", modify_owner)

        self.owner = modify_owner


    def captureHistoryID(self, page):
        historyID = re.findall("\d{1,15}:.*", page)
        modify_historyID = []

        for item in historyID:
            modify_historyID.append(re.sub(":.*", "", item))

        self.historyID = modify_historyID



    def captureSubject(self, page):

        # Should have only one subject per ticket.
        subject = re.findall("Subject: .*", page)
        modify_subject = ''.join(subject)

        #This should already be the subject we will analyze later.
        modify_subject = re.sub("Subject: ", "", modify_subject)

        self.subject = modify_subject


    def captureEmails(self, page):
                
        #Never going to have more than one creator.
        emails = re.findall("\d{1,12}: Correspondence added by .*", page)
        modify_emails = []

        for e in emails:
            e = re.sub("\d{1,12}: Correspondence added by ","", e)
            modify_emails.append(e)
            
        self.emails = modify_emails
        

    def captureComments(self, page):
        
        #Never going to have more than one creator.
        comments = re.findall("\d{1,12}: Comments added by .*", page)
        modify_comments = []

        for e in comments:
            e = re.sub("\d{1,12}: Comments added by ","", e)
            modify_comments.append(e)
            
        self.comments = modify_comments
        

    def captureCreated(self, page):

        #Never going to have more than one creator.
        created = re.findall("\d{1,12}: Ticket created by .*", page)
        modify_created = []

        #This should be the agents name        
        for e in created:
            e = re.sub("\d{1,12}: Ticket created by ","", e)
            modify_created.append(e)

        #If we come across a ticket created by Quickticket replace
        #the formhelper creator with the real creator.
        for item in modify_created:
            if item == 'formhelper':
                response = br.open(url + 'ticket/' + self.num + '/history/id/' + self.historyID[0])
                item_history = response.read()

                history_creator = re.findall("Ticket created by: .*", item_history)

                modify_history_creator = []

                for e in history_creator:
                    modify_history_creator.append(re.sub("Ticket created by: ", "", e))

                self.createdBy = modify_history_creator
                return

            else:
                self.createdBy = modify_created
                return


    def captureResolved(self, page):

        resolved = re.findall("\d{1,12}: Status changed from 'open' to 'resolved' by .*", page)
        modify_resolved = []

        for e in resolved:
            e = re.sub("\d{1,12}: Status changed from 'open' to 'resolved' by ","", e)
            modify_resolved.append(e)
                        
        self.resolvedBy = modify_resolved


    def calculateResolveTime(self, page):
        
        #Creates a list object with all strings matching the regular expression
        created = re.findall("Created: .*", page)

        #Join all list objects into one string
        modify_created = ''.join(created)

        #Strip out the Created.
        strip_created = modify_created.strip('Created: ')

        #Creates a datetime object with the time the ticket was created.
        created_time = datetime.strptime(strip_created, '%a %b %d %H:%M:%S %Y')
     
        #Creates a list object with all strings matching the regular expression
        resolved = re.findall("Resolved: .*", page)

        #Join all list objects into one string
        modify_resolved = ''.join(resolved)

        #Strip out the Resolved:
        strip_resolved = modify_resolved.strip('Resolved: ')
            
        #Now find the difference between the times.
        if strip_resolved != 'Not set':
            resolved_time = datetime.strptime(strip_resolved, '%a %b %d %H:%M:%S %Y')
        else:
            resolved_time = datetime.now()

        time_open = resolved_time - created_time
        self.timeOpen = self.convert_timedelta(time_open)


    def ticketHistory(self, page):

        self.captureHistoryID(page) 
        self.captureCreated(page)
        self.captureResolved(page)
        self.captureComments(page)
        self.captureEmails(page)


    def ticketShow(self, page):

        self.calculateResolveTime(page)
        self.captureSubject(page)
        self.captureOwner(page)


    def proccessHistory(self):
        
        response = br.open(url + 'ticket/' + self.num + '/history')
        page = response.read()

        self.ticketHistory(page)
        
        #print page

        
    def proccessShow(self):

        #Use mechanize to open up our desired page.
        response = br.open(url + 'ticket/' + self.num + '/show')

        #Save the page.
        page = response.read()

        self.ticketShow(page)

        #print page


    def proccessTicket(self, ticket, passed_br, passed_url):

        # What this currently does when proccessing the "Show" information.
        # 1. Returns the amount of time a ticket has been open or took to resolve
        # with float hours.
        #
        # 2. Extracts a ticket's creators, resolvers, commentors, corresponders,
        #    and subject.
        global br
        br = passed_br

        global url
        url = passed_url


        self.num = ticket
        self.proccessShow()
        self.proccessHistory()
"""
        print "Subject: ", self.subject
        print "Owner: ", self.owner
        print "Created by: ", self.createdBy
        print "History IDs: ", self.historyID
        print "Comments: ", self.comments
        print "Emails: ", self.emails
        print "Resolved by: ", self.resolvedBy
        print "Hours open: ", self.timeOpen

"""
