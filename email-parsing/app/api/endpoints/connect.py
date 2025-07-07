from fastapi import APIRouter, Depends
from app.models.schemas import ConnectResponse
from app.api.deps import get_settings
from app.services.gmail_service import GmailService
import logging

router = APIRouter()

@router.post("/")
async def connect_gmail(settings=Depends(get_settings)) -> ConnectResponse:
    logging.info("Starting Gmail connection attempt")
    gmail_service = GmailService(settings.EMAIL_ADDRESS, settings.APP_PASSWORD)
    success, message = await gmail_service.connect()
    logging.info(f"Gmail connection status: {message}")
    return ConnectResponse(success=success, message=message)
