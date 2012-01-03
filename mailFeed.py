import imaplib
from mailutils import *
from time import sleep, time

__all__ = ('dataFeed', 'mailFeed', 'attachmentsFeed', 'login')

def stdLog(x):
    print(x)
def errLog(x):
    print(x)

default_username = ''
default_password = ''
default_host = 'imap.gmail.com'

def login(username = default_username, password = default_password,
        host = default_host, inbox="INBOX"):
    """
    Connects to IMAP server and enters inbox
    Inputs:
        username : "joe.schmoe"
        password : "password1234"
        host : "imap.gmail.com"

    Outputs:
        an mbox object imaplib.IMAP4_SSL(imap.gmail.com)
        """

    stdLog('Logging into %s under username %s\n\n'%(host,username))
    mbox = imaplib.IMAP4_SSL(host)
    mbox.login(username, password)
    mbox.create("DownloadedMails")
    mbox.select(inbox)
    return mbox

def clearMessage(mbox, emailid):
    """
    Deletes message from imap server. Moves to "DownloadedMails" folder
    mbox - a mailbox or server returned from login or IMAP4_SSL object
    emailid - id (number or numeric string) of email to delete
    """
    mbox.copy(emailid, 'DownloadedMails')
    mbox.store(emailid, "+FLAGS.SILENT", '(\\Deleted)')

def dataFeed(waittime=60, **kwargs):
    """
    Generates a feed of raw email data from a mail server.
    See login function for keyword arguments to specify server
    Creates a generator/infinite list

    >>> feed = dataFeed(username='sam', password='123', host='imap.gmail.com')
    >>> for raw_data in feed:
    ...     print raw_data

    See Also:
        login
        mailFeed
        attachmentFeed
    """
    mbox = login(**kwargs)

    lastCheckTime = time()
    while(1): # Do forever
        try:
            newEmails = getEmailsFromServer(mbox)
            lastCheckTime = time()
            for mail in newEmails:
                yield mail
        except:
            errLog('Email Login Failed - Retrying')
            mbox = login() #maybe our authentication wore out?

        # Compute sleep time
        timeSinceLastCheck = time() - lastCheckTime
        sleepTime = waittime - timeSinceLastCheck
        if sleepTime > 0:
            sleep(sleepTime)

def getEmailsFromServer(mbox):
    """
    Fetch and return all new email from an mbox server
    Returns raw e-mail data. Parse using mailFromData function
    """

    mbox.select('INBOX')

    # Collect the IDs of all emails in the inbox
    resp, items = mbox.search(None, 'ALL')
    items = items[0].split()

    dataPackets = []
    for emailid in items:
        response, data = mbox.fetch(emailid, "(RFC822)")

        if response != 'OK':
            errlog('Failed on message '+str(emailid))
        else:
            dataPackets.append(data)
            clearMessage(mbox, emailid) # remove email from online inbox

    return dataPackets

def mailFeed(*args, **kwargs):
    """
    See runs mailFromData on dataFeed stream

    See Also:
        dataFeed
    """
    return (mailFromData(data) for data in dataFeed(*args, **kwargs))

def attachmentsFeed(*args, **kwargs):
    """
    See runs getAttachments on mailFeed stream

    See Also:
        dataFeed
    """
    return (getAttachments(mail) for mail in mailFeed(*args, **kwargs))
