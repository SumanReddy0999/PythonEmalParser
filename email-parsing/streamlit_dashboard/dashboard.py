import streamlit as st
import requests

st.set_page_config(page_title="Email Research Dashboard", layout="wide")

BASE_URL = "http://localhost:8000"

st.title("📬 Email Company Research & Credibility Dashboard")

# Run orchestration only on button click
if st.button("🚀 Start Parsing"):
    with st.spinner("Fetching and researching unread emails..."):
        try:
            response = requests.post(f"{BASE_URL}/orchestrate/orchestrate/")
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to fetch data: {e}")
            st.stop()

    if not data:
        st.info("ℹ️ No research reports available.")
        st.stop()

    # Sort companies by credibility score (descending)
    sorted_reports = sorted(
        data,
        key=lambda r: r.get("credibility", {}).get("score", 0),
        reverse=True
    )

    for report in sorted_reports:
        with st.expander(f"📧 {report['company_name']}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("🏢 Company Profile")
                st.markdown(f"**Name:** {report['company_profile']['name']}")
                st.markdown(f"**Description:** {report['company_profile'].get('description', 'N/A')}")
                st.markdown(f"**Website:** {report['company_profile'].get('website', 'N/A')}")

                st.subheader("💡 Key Insights")
                for insight in report.get("key_insights", []):
                    st.markdown(f"- {insight}")

                st.subheader("📌 Recommendations")
                for reco in report.get("recommendations", []):
                    st.markdown(f"- {reco}")

            with col2:
                st.subheader("🔎 Credibility Score")
                score_data = report.get("credibility", {})
                score = score_data.get("score", "N/A")
                st.metric("Score", score)

                st.write("### 📈 Metrics")
                raw_metrics = score_data.get("raw_metrics", {})

                # Display formatted values (no raw scores)
                for factor, value in raw_metrics.items():
                    if factor == "market_cap" and isinstance(value, (int, float)):
                        value_str = f"${value / 1e9:.2f}B"
                    elif factor in ["age_years", "domain_age"] and isinstance(value, (int, float)):
                        value_str = f"{value} years"
                    elif isinstance(value, float):
                        value_str = f"{value:.2f}"
                    elif value is True:
                        value_str = "Yes"
                    elif value is False:
                        value_str = "No"
                    elif value in [None, "N/A"]:
                        value_str = "Unknown"
                    else:
                        value_str = str(value)

                    label = factor.replace("_", " ").replace("years", "").title().strip()
                    st.markdown(f"- **{label}:** {value_str}")
