from suds.client import Client
from suds.wsse import *
import pprint
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import datetime

#getAllUsersLastLogin(xs:string userLoginId, )

threeMonths = date.today() + relativedelta(months=-3)

url = 'https://login.swiftkanban.com/axis2/services/TeamMemberService?wsdl'
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
pprint.pprint(loginInfo)


def compareDates(lastLoginInfo, currentDate):
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
    #return usersToMessage

def sortLoginDates(lastLogInInfo, currentDate):
    {}

theUsers = compareDates(loginInfo, threeMonths)

print theUsers