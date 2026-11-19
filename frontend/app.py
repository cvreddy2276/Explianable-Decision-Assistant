"""Professional Streamlit interface for the Explainable Decision Assistant."""

import json
import os
from typing import Any, Dict

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/explain")

st.set_page_config(
    page_title="Explainable Decision Assistant",
    page_icon=":mag:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main { background-color: #f7f9fc; }
    .block-container { max-width: 1100px; }
    [data-testid="stMetric"] { background: white; border-radius: 10px; padding: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Explainable Decision Assistant")
st.caption("Understand operational decisions through simple, transparent explanations")

default_decision: Dict[str, Any] = {
    "employee": "Rahul",
    "experience": 5,
    "traffic_score": 0.3,
    "distance": 15,
    "assigned_route": "Zone A",
}

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("Decision Data")
    decision_text = st.text_area(
        "Paste operational decision data as JSON",
        value=json.dumps(default_decision, indent=2),
        height=330,
    )
    run_button = st.button("Run Explanation", type="primary", use_container_width=True)

with right:
    st.subheader("Report")
    report_placeholder = st.container()

if run_button:
    try:
        decision = json.loads(decision_text)
        if not isinstance(decision, dict):
            raise ValueError("Top-level JSON value must be an object.")

        with st.spinner("The agents are analyzing the decision..."):
            response = requests.post(API_URL, json=decision, timeout=90)

        if response.status_code != 200:
            detail = response.json().get("detail", response.text)
            st.error(f"API error ({response.status_code}): {detail}")
        else:
            report = response.json()
            with report_placeholder:
                st.markdown("### Decision Explanation")
                st.info(report["decision_explanation"])

                st.markdown("### Fairness Assessment")
                fairness = report["fairness_assessment"]
                if fairness.lower().startswith("the decision appears fair"):
                    st.success(fairness)
                else:
                    st.warning(fairness)

                st.markdown("### Influencing Factors")
                factors = report["influencing_factors"]
                if factors:
                    st.write(" • " + "\n • ".join(factors))
                else:
                    st.write("No factors were identified.")

                st.markdown("### Final Summary")
                st.success(report["final_summary"])
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON: {exc.msg}")
    except requests.RequestException as exc:
        st.error(
            "Could not connect to the FastAPI backend. "
            "Start it with: uvicorn backend.main:app --reload"
        )
        st.caption(str(exc))
    except (KeyError, ValueError) as exc:
        st.error(str(exc))
