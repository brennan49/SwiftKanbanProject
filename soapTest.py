from suds.client import Client
from suds.wsse import *
import pprint

#getAllUsersLastLogin(xs:string userLoginId, )

url = 'https://login.swiftkanban.com/axis2/services/TeamMemberService?wsdl'
client = Client(url)

security = Security()
token = UsernameToken('devlin.brennan@optum.com', 'devBrenn49')
security.tokens.append(token)
client.set_options(wsse=security)

result = client.service.getAllActiveUsersInOrg('devlin.brennan@optum.com')
aUser = result[0][1]["_loginId"]
listUsers = result[0]
users = []
for x in listUsers:
    users.append(x["_loginId"])


lastLogin = client.service.getAllUsersLastLogin('devlin.brennan@optum.com', users)

loginInfo = lastLogin[0]
pprint.pprint(loginInfo)
loginList = []
for x in loginInfo:
    loginList.append([x["_userName"], x["_emailAddress"], x["_lastLoginDate"]])

for i in loginList:
    print(loginList[i])