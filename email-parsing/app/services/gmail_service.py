import logging
import imaplib
import email
from email.header import decode_header
from typing import List, Dict
import aiosqlite
import asyncio

class GmailService:
    def __init__(self, email_address: str, app_password: str):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = "imap.gmail.com"
        self.imap = None

    async def connect(self):
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.email_address, self.app_password)
            logging.info("Connected to Gmail IMAP server")
            return True, "Connected successfully"
        except Exception as e:
            logging.error(f"Gmail connection error: {e}")
            return False, str(e)

    async def fetch_unread_emails(self) -> List[Dict]:
        emails = []
        try:
            self.imap.select("INBOX")
            status, messages = self.imap.search(None, '(UNSEEN)')
            if status != "OK":
                logging.warning("Failed to search for unread emails")
                return emails
            for num in messages[0].split():
                status, data = self.imap.fetch(num, '(RFC822)')
                if status != "OK":
                    continue
                msg = email.message_from_bytes(data[0][1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                from_ = msg.get("From")
                date = msg.get("Date")
                snippet = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get("Content-Disposition"))
                        if ctype == "text/plain" and "attachment" not in cdispo:
                            snippet = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    snippet = msg.get_payload(decode=True).decode(errors="ignore")
                emails.append({
                    "id": num.decode(),
                    "subject": subject,
                    "from": from_,
                    "date": date,
                    "snippet": snippet[:500]  # limit snippet length
                })
        except Exception as e:
            logging.error(f"Error fetching emails: {e}")
        return emails
