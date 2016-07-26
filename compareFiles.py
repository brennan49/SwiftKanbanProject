import sys
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pprint
import ast

def compareFiles(newFile, originalFile):
    #try:
     #   file = open(originalFile, 'r')
    #except IOError:
     #   print('There was an error opening the file!')
     #   sys.exit()
    with open(newFile, 'r') as file1:
        with open(originalFile, 'r') as file2:
            same = set(file1).intersection(file2)
    same.discard('\n')
    with open('Users_to_Delete.txt', 'w') as file_out:
        for line in same:
            file_out.write(line)


def collectUserToDelete(usersToDeleteFile):
    with open(usersToDeleteFile) as f:
        content = json.load(f)
    #pprint.pprint(content)
    userEmails = []
    for users in content:
        #ast.literal_eval(users)
        userEmails.append(users['emailAddress'])
    return userEmails

def overwriteFile(newFile, oldFile):
    {}

def messageUsersToDelete(sender, toaddr):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = toaddr
    msg['Subject'] = 'Automated message regarding your SwiftKanban Account'

    body = """Hello,

If you have recieved this message, it means that you have not responded to our emails to
either log into your SwiftKanban account or emailed us to have it deleted so we have automatically
put your account onto our list of those to delete. If you still wish to keep your account inform us
by sending a message to swift.users@optum.com as soon as possible.

Thank you
    """
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('mailo2.uhc.com', 25)
    text = msg.as_string()
    server.sendmail(sender, toaddr, text)
    server.quit()

def main():
    compareFiles("newUserFile.txt", "pastUserFile.txt")
    deleteUsers = collectUserToDelete("New_User_List")
    users = [u'devlin.brennan@optum.com', u'tien.bui@optum.com']
    for theUser in users:
        messageUsersToDelete("swift.users@optum.com", theUser)
    #for user in deleteUsers:
        #messageUsersToDelete("swift.users@optum.com", user)
    pprint.pprint(deleteUsers)

main()