from fastapi import APIRouter, Depends
from app.api.deps import get_settings
from app.services.email_reader import EmailReader
from app.services.research_engine import ResearchEngine
from app.models.schemas import ResearchReport
from app.utils.extract import extract_company_names
from typing import List
from app.core.config import Settings

router = APIRouter()

@router.post("/orchestrate/", response_model=List[ResearchReport])
async def orchestrate(settings: Settings = Depends(get_settings)):
    reader = EmailReader(settings.EMAIL_ADDRESS, settings.APP_PASSWORD)

    
    # Ensure fetch_unread_emails is synchronous or wrap it in asyncio if needed
    emails = reader.fetch_unread_emails()
    print("Fetched Emails:\n", emails)


    company_names = extract_company_names(emails)
    
    engine = ResearchEngine(settings.openai_api_key, settings.serper_api_key, settings.model)

    results = []
    for name in company_names:
        try:
            report = await engine.research_company(name)
            if report:
                results.append(report)
        except Exception as e:
            print(f"Failed to research {name}: {e}")

    return results
