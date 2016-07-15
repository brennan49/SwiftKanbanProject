from suds.client import Client
from suds.wsse import *
import pprint
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#C:\Python27\python.exe C:\Users\dbrennan\PycharmProjects\SwitfKanban_Project\soapTest.py

#Communicates with SwiftKanban servers to get a list of all users that have not logged
#in in longer than 3 moths
def getUsersToMessage():
    url = 'https://login.swift-kanban.com/axis2/services/TeamMemberService?wsdl'
    client = Client(url)

    security = Security()
    token = UsernameToken('devlin.brennan@optum.com', 'devBrenn49')
    security.tokens.append(token)
    client.set_options(wsse=security)

    result = client.service.getAllActiveUsersInOrg('devlin.brennan@optum.com')
    listUsers = result[0]
    users = []
    for x in listUsers:
        users.append(x["_loginId"])
    lastLogin = client.service.getAllUsersLastLogin('devlin.brennan@optum.com', users)
    loginInfo = lastLogin[0]
    #pprint.pprint(loginInfo)
    return loginInfo

#Once list of users that haven't logged in in 3+ months, sort them into dictionaries
#of just username and email.
def sortUsers(lastLoginInfo, currentDate):
    usersToMessage = []
    for date in lastLoginInfo:
        theDate = date["_lastLoginDate"]
        lastLogin = theDate.split("T")
        currentDate = str(currentDate)
        lastLogin = str(lastLogin[0])
        threeMonths = datetime.strptime(currentDate, '%Y-%m-%d')
        lastLogged = datetime.strptime(lastLogin, '%Y-%m-%d')
        if(lastLogged < threeMonths):
            usersToMessage.append({"username": date["_userName"], "emailAddress": date["_emailAddress"]})
    return usersToMessage

def sendMail(sender, toaddr):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = toaddr
    msg['Subject'] = 'Automated message regarding your SwiftKanban Account'

    body = """Hello,

If you have recieved this message, it means that you have not logged into
SwiftKanban in 3+ months.  As we would like to reattain these licenses for the
software, we ask you that please either e-mail devlin.brennan@optum.com to have your account deleted
if you no longer need it else, please log into your account.

This message is set up to run once a month for people that have not logged in in over
a month.

Thank you
"""
    msg.attach(MIMEText(body, 'plain'))
    #what are these values below for optum's servers?
    server = smtplib.SMTP('mailo2.uhc.com', 25)
    text = msg.as_string()
    server.sendmail(sender, toaddr, text)
    server.quit()

def main():
   theUsers = getUsersToMessage()
   threeMonths = date.today() + relativedelta(months=-3)
   messageUsers = sortUsers(theUsers, threeMonths)
   #pprint.pprint(messageUsers)
   userEmails = []
   for users in messageUsers:
       userEmails.append(users["emailAddress"])
   pprint.pprint(userEmails)
   sendees = ["devlin.brennan@optum.com", "tien.bui@optum.com", "michael_blaha@optum.com"]
   for sendee in sendees:
       sendMail("devlin.brennan@optum.com", sendee)

main()