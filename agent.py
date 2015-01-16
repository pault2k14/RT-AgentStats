class agent(object):
    name = ""
    ticketsCreated = 0
    ticketsResolved = 0
    totalCommenents = 0
    totalEmail = 0
    totalWalkin = 0
    totalPhone = 0        
    
    # The class "constructor" - It's actually an initializer 
    def __init__(self, name, ticketsCreated, ticketsResolved, totalComments, totalEmail, totalWalkin, totalPhone):
        self.name = name
        self.ticketsCreated = ticketsCreated
        self.ticketsResolved = ticketsResolved
        self.totalComments = totalComments
        self.totalEmails = totalEmail
        self.totalWalkin = totalWalkin
        self.totalPhone = totalPhone

def make_agent(name, ticketsCreated, ticketsResolved, totalComments, totalEmail, totalWalkin, totalPhone):
    agent = agent(name, age, major)
    return agent
