import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Email Orchestrator", layout="wide")
st.title("📨 Email Orchestrator Dashboard")

# Fetch Unread Emails
st.header("📧 Unread Emails")
if st.button("Fetch Unread Emails"):
    response = requests.get(f"{BASE_URL}/fetch/")
    if response.status_code == 200:
        emails = response.json().get("emails", [])
        if not emails:
            st.info("No unread emails found.")
        else:
            for email in emails:
                st.markdown(f"**From:** {email['sender']} | **Subject:** {email['subject']}")
    else:
        st.error("Failed to fetch emails")

# Run Research
st.header("🔍 Company Research & Credibility Scoring")
if st.button("Run Orchestration"):
    response = requests.post(f"{BASE_URL}/orchestrate/orchestrate/")
    if response.status_code == 200:
        reports = response.json()
        if not reports:
            st.warning("No companies extracted from emails.")
        else:
            for report in reports:
                st.subheader(f"🏢 {report['company_name']}")
                st.markdown(f"**Research Date:** {report['research_date']}")
                st.markdown(f"**Status:** {report['overall_status']} | **Completion:** {report['completion_percentage']}%")

                profile = report.get("company_profile", {})
                st.markdown(f"**Description:** {profile.get('description', 'N/A')}")

                # Fake Credibility Scores (replace with real logic)
                company_age_score = 20
                market_cap_score = 20
                employee_score = 20
                profile_score = 20
                total_score = company_age_score + market_cap_score + employee_score + profile_score

                st.markdown("### 🧠 Credibility Breakdown")
                st.progress(total_score / 100)
                st.write(f"**Final Score:** {total_score}/100")

                with st.expander("🔍 Breakdown"):
                    st.write(f"Company Age Score: {company_age_score}/25")
                    st.write(f"Market Cap Score: {market_cap_score}/25")
                    st.write(f"Employee Score: {employee_score}/25")
                    st.write(f"Online Profile Score: {profile_score}/25")
    else:
        st.error("Failed to perform research")
