import email

def addrFromMail(mail):
    """
    Scrapes the senders email address from the mail message
    """
    return email.Utils.parseaddr(mail['From'])[1].lower()

def mailFromData(data):
    """
    Safely obtains the mail object from the data sent by the imap server
    """
    email_body = data[0][1]
    mail = email.message_from_string(email_body)
    return mail

counter = 0
def getAttachments(mail):
    """
    Given a mail object return a list of attachments

    Returns list of (filename, data payload) pairs
    """
    if mail.get_content_maintype() != 'multipart':
       return []

    results = []
    for part in mail.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if not filename: #anonymous file
            filename = 'part-%03d%s' % (counter, 'bin')
            counter += 1
        results.append( (filename, part.get_payload(decode=True)) )
    return results
