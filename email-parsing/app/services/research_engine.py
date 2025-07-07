import uuid
import logging
import json
import re
from datetime import datetime
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from pydantic import Field

from app.models.schemas import ResearchReport, CompanyProfile
from app.utils.credibility import compute_credibility_score


class SerperSearchTool(BaseTool):
    name: str = "serper_search"
    description: str = "Google search tool using Serper API"
    api_key: str = Field(...)

    def _run(self, query: str) -> str:
        import asyncio
        return asyncio.run(self._arun(query))

    async def _arun(self, query: str) -> str:
        import httpx
        headers = {"X-API-KEY": self.api_key}
        params = {"q": query, "num": 3}
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://google.serper.dev/search", headers=headers, params=params)
            if resp.status_code == 200:
                results = resp.json().get("organic", [])
                return "\n".join(f"{r.get('title', '')}: {r.get('snippet', '')}" for r in results)
            else:
                return f"Serper error: {resp.status_code}"


def extract_json_block(text: str) -> Optional[dict]:
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        return json.loads(match.group()) if match else None
    except Exception as e:
        logging.warning(f"❌ JSON extraction failed: {e}")
        return None


class ResearchEngine:
    def __init__(self, openai_api_key: str, serper_api_key: str, model: str):
        self.openai_api_key = openai_api_key
        self.serper_api_key = serper_api_key
        self.model = model

        self.llm = ChatOpenAI(api_key=openai_api_key, model=model, temperature=0)
        self.search_tool = SerperSearchTool(api_key=serper_api_key)
        self.reports = {}

    async def research_company(self, company_name: str) -> Optional[ResearchReport]:
        logging.info(f"🚀 Starting research for: {company_name}")
        search_results = await self.search_tool._arun(f"{company_name} company profile")

        # Step 1: Company Profile
        profile_prompt = f"Write a concise factual company profile for '{company_name}' using this data:\n\n{search_results}"
        profile_response = await self.llm.ainvoke(profile_prompt)
        profile_text = profile_response.content.strip()

        # Step 2: Extract Metrics (with 'founded_year')
        metrics_prompt = (
            f"Based on this info about '{company_name}', estimate realistic values for the following metrics.\n"
            f"Respond ONLY with JSON in this format (no extra text):\n"
            "{\n"
            "  \"founded_year\": 2004,\n"
            "  \"market_cap\": 150000000000,\n"
            "  \"employees\": 10000,\n"
            "  \"domain_age\": 15,\n"
            "  \"sentiment_score\": 0.85,\n"
            "  \"certified\": true,\n"
            "  \"funded_by_top_investors\": true\n"
            "}\n\n"
            f"Search results:\n{search_results}"
        )

        metrics_response = await self.llm.ainvoke(metrics_prompt)
        raw_text = metrics_response.content.strip()
        logging.info(f"🧾 Raw LLM metrics response:\n{raw_text}")

        raw_metrics = extract_json_block(raw_text)
        logging.info(f"📊 Parsed metrics: {raw_metrics}")

        if not raw_metrics:
            logging.warning("⚠️ Using fallback values due to invalid LLM response")
            raw_metrics = {
                "age_years": 5,
                "market_cap": 1e9,
                "employees": 500,
                "domain_age": 5,
                "sentiment_score": 0.6,
                "certified": True,
                "funded_by_top_investors": False
            }
        else:
            # Convert founded_year → age_years
            if "founded_year" in raw_metrics:
                try:
                    current_year = datetime.utcnow().year
                    raw_metrics["age_years"] = max(current_year - int(raw_metrics.pop("founded_year")), 0)
                except Exception as e:
                    logging.warning(f"⚠️ Failed to convert founded_year to age_years: {e}")
                    raw_metrics["age_years"] = 5

        # Step 3: Score Calculation
        credibility_score, score_breakdown = compute_credibility_score(**raw_metrics)

        # Step 4: Assemble Report
        report_id = str(uuid.uuid4())
        profile = CompanyProfile(name=company_name, description=profile_text, website=None)

        report = ResearchReport(
            report_id=report_id,
            company_name=company_name,
            research_date=datetime.utcnow(),
            overall_status="completed",
            completion_percentage=100.0,
            company_profile=profile,
            products_services=None,
            market_analysis=None,
            financial_metrics=[{"credibility_score": credibility_score}],
            key_insights=[
                "Generated using Serper + OpenAI",
                f"Credibility Score: {credibility_score}"
            ],
            recommendations=["Verify insights with official sources for critical decisions."],
            credibility={
                "score": credibility_score,
                "raw_metrics": raw_metrics,
                "score_breakdown": score_breakdown
            }
        )

        self.reports[report_id] = report
        logging.info(f"✅ Completed research for {company_name} — Score: {credibility_score}")
        return report

    async def get_report(self, report_id: str) -> Optional[ResearchReport]:
        return self.reports.get(report_id)
