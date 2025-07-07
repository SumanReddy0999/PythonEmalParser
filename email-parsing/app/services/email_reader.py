import imaplib
import email
from email.header import decode_header

class EmailReader:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password
        self.server = "imap.gmail.com"

    def fetch_unread_emails(self):
        mail = imaplib.IMAP4_SSL(self.server)
        mail.login(self.user, self.password)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()

        emails = []
        for num in email_ids:
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            from_ = msg.get("From")
            emails.append({"from": from_, "subject": subject})

        mail.logout()
        return emails
