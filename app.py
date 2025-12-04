
import streamlit as st
from enterprise_onboarding import run_sequential_agents  

st.set_page_config(page_title="Enterprise Onboarding Agent", layout="centered")
st.title("Enterprise Onboarding Agent System")
st.markdown("##### Powered by Gemini 1.5 Flash + Multi-Agent Workflow")

with st.form("onboarding_form"):
    st.write("### New Employee Details")
    name = st.text_input("Full Name", "Jane Doe")
    role = st.text_input("Job Role", "Senior Software Engineer")
    email = st.text_input("Email", "jane@company.com")
    start_date = st.date_input("Start Date", value=None)

    submitted = st.form_submit_button("Start Onboarding 🚀")

    if submitted:
        if not name or not email:
            st.error("Name and Email are required!")
        else:
            with st.spinner("HR → IT → Manager agents are working..."):
                result = run_sequential_agents(
                    {
                        "name": name,
                        "role": role,
                        "email": email,
                        "start_date": str(start_date)
                    },
                    f"onboarding_{name.lower().replace(' ', '_')}"
                )

            st.success("Onboarding Completed Successfully!")
            st.json(result, expanded=True)