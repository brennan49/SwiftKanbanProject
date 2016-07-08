from suds.client import Client
from suds.wsse import *
import pprint
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#getAllUsersLastLogin(xs:string userLoginId, )

threeMonths = date.today() + relativedelta(months=-3)

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


def sortUsers(lastLoginInfo, currentDate):
    usersToMessage = []
    for date in lastLoginInfo:
        theDate = date["_lastLoginDate"]
        lastLogin = theDate.split("T")
        currentDate = str(currentDate)
        lastLogin = str(lastLogin[0])
        #print lastLogin
        threeMonths = datetime.strptime(currentDate, '%Y-%m-%d')
        lastLogged = datetime.strptime(lastLogin, '%Y-%m-%d')
        if(lastLogged < threeMonths):
            usersToMessage.append({"username": date["_userName"], "emailAddress": date["_emailAddress"]})

    return usersToMessage

theUsers = sortUsers(loginInfo, threeMonths)
"""
def sendMail(sender, userPass, toaddr):
    emailAddr = []
    for user in toaddr:
        emailAddr.append(user["emailAddress"])
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ", ".join(emailAddr)
    msg['Subject'] = 'Automated message'

    body = """"""
    msg.attach(MIMEText(body, 'plain'))
    #what are these values below for optum's servers?
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, userPass)
    text = msg.as_string()
    server.sendmail(msg.get("From"), emailAddr, text)
    print "Message Sent"
    server.quit()

sendees = [{"emailAddress": "devlin.brennan@optum.com"}, {"emailAddress": "intreeged@gmail.com"}]

sendMail("devlinbrennan@gmail.com", "Brenndev@49", sendees)"""

def sendMessage(sender, userPass, toaddr):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = toaddr
    msg['Subject'] = 'Automated message'

    body = """This is an automated test message to multiple parties.
              If you get this, please let me know, I would like to test out

              sending an e-mail with multiple lines and spaces.

              Thank you,

              Devlin
              """
    msg.attach(MIMEText(body, 'plain'))
    #what are these values below for optum's servers?
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, userPass)
    text = msg.as_string()
    server.sendmail(sender, toaddr, text)
    print "done"
    server.close()

sendees = ["devlinbrennan@gmail.com", "intreeged@gmail.com"]
for sendee in sendees:
    sendMessage("devlinbrennan@gmail.com", "Brenndev@49", sendee)

