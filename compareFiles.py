import sys
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename
import pprint


#Compares two files, one of new users to possible delete and the other a previous list
#of users to delete.  If a user is in both lists, that user will be deleted placed into a list
#for automatic deletion.
def compareFiles(newFile, originalFile):
    matchFound = False
    Users_To_Delete = []
    #Test that the file exists, if not create the file and fill it with the current list obtained and exit
    try:
        file = open(originalFile, 'r')
    except IOError:
        print('There was an error opening the file! It may not exist!')
        overWriteFile("New_User_List", "Past_User_List")
        sys.exit()
    #Test that the file is not empty if it is, fill it with the current list and exit
    if os.stat(originalFile).st_size == 0:
        print('The file is empty.')
        overWriteFile("New_User_List", "Past_User_List")
        sys.exit()
    #get the list of users
    with open(newFile, 'rU') as file1:
        f1 = file1.read()
        list1 = eval(f1)
    with open(originalFile, 'rU') as file2:
        f2 = file2.read()
        list2 = eval(f2)
    #Compare the two lists for similar entries
    for list1User in list1:
        for list2User in list2:
            if(list1User == list2User):
                matchFound = True
                Users_To_Delete.append(list1User)
    #If no matches found, replace old list with new list of users and exit
    if(matchFound == False):
        print "No comparisons found"
        overWriteFile("New_User_List", "Past_User_List")
        sys.exit()
    with open('Users_to_Delete', 'w') as file_out:
        json.dump(Users_To_Delete, file_out)


#After list of new users to delete and previous list of users have been compared,
#This function will iterate through the list of dictionaries and retrieve their email
#address's.
def collectUserToDelete(usersToDeleteFile):
    with open(usersToDeleteFile) as f:
        content = json.load(f)
    userEmails = []
    for users in content:
        userEmails.append(users['emailAddress'])
    return userEmails


#Overwrite the previous list of users to delete with the new list of users to delete once they
#have been informed that their account will be deleted
def overWriteFile(newFile, oldFile):
    with open(newFile, 'r') as file1:
        f1 = file1.read()
        list1 = eval(f1)
    with open(oldFile,'w+') as file2:
        json.dump(list1, file2)

def formatFile(theFile):
    with open(theFile, 'r') as file1:
        f1 = file1.read()
        list = eval(f1)
    with open("UserList", "w+") as file2:
        print >> file2, "\n".join(str(i) for i in list)


def messageUsersToDelete(sender, toaddr):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = toaddr
    msg['Subject'] = 'Automated message regarding your SwiftKanban Account'

    body = """Hello,

If you have recieved this message, it means that you have not logged into your SwiftKanban account for 3+ months and
will thus have your account deleted to recoup licenses. If you still wish to keep your account inform us
by sending a message to swift.users@optum.com as soon as possible.

Thank you
    """
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('mailo2.uhc.com', 25)
    text = msg.as_string()
    server.sendmail(sender, toaddr, text)
    server.quit()


#sends an email to whomever specified as admin for the SwiftKanban org at optum.  It will
#send them a formatted document of all of the users that have failed to respond to the automated
#emails asking them to log in or ask for their account to be deleted, and are thus to be
#forefully deleted by us.
def sendFile(theFile):
    msg = MIMEMultipart()
    msg['From'] = "swift.users@optum.com"
    msg['To'] = "swift.users@optum.com"
    msg['Subject'] = 'This is a Test'

#attach the body to the message to send can be modified to say whatever you want.
    body = """Hello,

Attached to this automated email is a list of users that have ignored warnings to log in or ask
for their email to be deleted.  As such they have been added to this list of users that will
be deleted in the next batch.

Thank you
        """
    msg.attach(MIMEText(body, 'plain'))

#this section opens the file with the user information and attaches it to the email to send
    with open(theFile, 'rb') as fil:
        part = MIMEApplication(
            fil.read(),
            Name=basename(theFile)
        )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(theFile)
        msg.attach(part)

#contains the server and port number for optum and sends the email
    server = smtplib.SMTP('mailo2.uhc.com', 25)
    text = msg.as_string()
    server.sendmail("swift.users@optum.com", "swift.users@optum.com", text)
    server.quit()


def main():
    compareFiles("New_User_List", "Past_User_List")
    deleteUsers = collectUserToDelete("Users_to_Delete")
    for user in deleteUsers:
        messageUsersToDelete("swift.users@optum.com", user)
    #format the Users_to_Delete file to be easier to read and place in a new file called UserList
    formatFile("Users_to_Delete")
    #Send the formatted file to our administrator or whomever takes care of deleting users
    sendFile("UserList")
    #overwrite past list of users to delete with the current new list for preparation when comparing
    #during the next time the program is run.
    overWriteFile("New_User_List", "Past_Users_List")

main()