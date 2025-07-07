from fastapi import APIRouter, Depends
from app.models.schemas import FetchEmailsResponse
from app.api.deps import get_settings
from app.services.gmail_service import GmailService
from app.services.email_parser import EmailParser
import logging

router = APIRouter()

@router.get("/")
async def fetch_unread_emails(settings=Depends(get_settings)) -> FetchEmailsResponse:
    logging.info("Fetching unread emails")
    gmail_service = GmailService(settings.EMAIL_ADDRESS, settings.APP_PASSWORD)
    connected, msg = await gmail_service.connect()
    if not connected:
        return FetchEmailsResponse(emails=[])
    raw_emails = await gmail_service.fetch_unread_emails()
    parsed_emails = EmailParser.parse_emails(raw_emails)
    logging.info(f"Fetched {len(parsed_emails)} unread emails")
    return FetchEmailsResponse(emails=parsed_emails)
