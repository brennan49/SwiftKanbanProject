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
    token = UsernameToken('SAM_SK_LOGIN', 'SAMS_SK_LOGIN')
    security.tokens.append(token)
    client.set_options(wsse=security)
    result = client.service.getAllActiveUsersInOrg('SAM_SK_LOGIN')
    listUsers = result[0]
    users = []
    for x in listUsers:
        users.append(x["_loginId"])
    lastLogin = client.service.getAllUsersLastLogin('SAM_SK_LOGIN', users)
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


#This sends an automated email to all of the users that have not logged in in 3+ months
def sendMail(sender, toaddr):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = toaddr
    msg['Subject'] = 'Automated message regarding your SwiftKanban Account'

    body = """Hello,

You are receiving this email because you have not logged into your SwiftKanban account in 3 or more months.
If you would like to keep your account please log in now.  This message will be sent out once a week every Friday.
If you do not log in or no longer need you account, you will be placed into a list to have your account deleted at the
end of every month

Thank you
"""
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('mailo2.uhc.com', 25)
    text = msg.as_string()
    server.sendmail(sender, toaddr, text)
    server.quit()

#creates a file containing a list of all of the users that have not logged in in 3+ months.
def fileOutput(userInfo):
    with open("New_User_List", "w+") as file_handler:
        json.dump(userInfo,file_handler)

def main():
   theUsers = getUsersToMessage()
   threeMonths = date.today() + relativedelta(months=-3)
   messageUsers = sortUsers(theUsers, threeMonths)
   fileOutput(messageUsers)
   userEmails = []
   for users in messageUsers:
       userEmails.append(users["emailAddress"])
   for sendee in userEmails:
       sendMail("swift.users@optum.com", sendee)

main()