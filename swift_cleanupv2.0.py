from suds.client import Client
from suds.wsse import *
import pprint
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

#C:\Python27\python.exe C:\Users\dbrennan\PycharmProjects\SwitfKanban_Project\swift_cleanup.py

#Communicates with SwiftKanban servers to get a list of all users that have not logged
#in in longer than 3 months
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
            usersToMessage.append({"username": "{0}".format(date["_userName"]), "emailAddress": "{0}".format(date["_emailAddress"])})
    #pprint.pprint(usersToMessage)
    return usersToMessage

def sendMail(sender, toaddr):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = toaddr
    msg['Subject'] = 'Automated message regarding your SwiftKanban Account'

    body = """Hello,

If you have recieved this message, it means that you have not logged into
SwiftKanban in 3+ months.  As we would like to reattain these licenses for the
software, we ask you that please either e-mail swift.users@optum.com to have your account deleted
if you no longer need it else, please log into your account.

This message is set up to run once a month for people that have not logged in in over
a month.

Thank you
"""
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('mailo2.uhc.com', 25)
    text = msg.as_string()
    server.sendmail(sender, toaddr, text)
    server.quit()

def fileOutput(userInfo):
    with open("New_User_List", "w+") as file_handler:
        json.dump(userInfo,file_handler)

def main():
   theUsers = getUsersToMessage()
   threeMonths = date.today() + relativedelta(months=-3)
   messageUsers = sortUsers(theUsers, threeMonths)
   fileOutput(messageUsers)
   #userEmails = []
   #for users in messageUsers:
   #    userEmails.append(users["emailAddress"])
   #for sendee in userEmails:
    #   sendMail("swift.users@optum.com", sendee)
   #sendMail("swift.users@optum.com", "devlin.brennan@optum.com")

main()