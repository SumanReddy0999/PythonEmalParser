from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime


class ConnectResponse(BaseModel):
    success: bool
    message: str


class Email(BaseModel):
    id: str
    subject: str
    sender: EmailStr
    date: datetime
    snippet: str


class FetchEmailsResponse(BaseModel):
    emails: List[Email]


class CompanyProfile(BaseModel):
    name: str
    description: Optional[str]
    website: Optional[str]


class CredibilityScore(BaseModel):
    score: float  # 🔁 Changed from int to float
    raw_metrics: Dict[str, Any]  # e.g., {"age_years": 5, "market_cap": 1e9}
    score_breakdown: Dict[str, float]  # e.g., {"age": 7.5, "market_cap": 10.0}


class ResearchReport(BaseModel):
    report_id: str
    company_name: str
    research_date: datetime
    overall_status: str
    completion_percentage: float
    company_profile: CompanyProfile
    products_services: Optional[List[Any]]
    market_analysis: Optional[Any]
    financial_metrics: Optional[List[Any]]
    key_insights: Optional[List[str]]
    recommendations: Optional[List[str]]
    credibility: Optional[CredibilityScore]
