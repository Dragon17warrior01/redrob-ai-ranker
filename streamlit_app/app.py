"""
Streamlit Frontend
Redrob AI Candidate Ranking System
"""

import time
from pathlib import Path

import pandas as pd
import streamlit as st

from pipeline_runner import run_pipeline
from rank import rank_candidates
from rank import export_csv


st.set_page_config(
    page_title="Redrob AI Candidate Ranking",
    page_icon="🤖",
    layout="wide",
)

OUTPUT_CSV = Path("output/top_100_candidates.csv")


st.title("🤖 Redrob AI Candidate Ranking System")

st.markdown(
    """
This application ranks candidates using the existing LangGraph pipeline.

### Features

- Parse Job Description
- Evaluate 100,000 Candidates
- Technical Scoring
- Behavioral Scoring
- Consistency Detection
- Honeypot Penalty
- Final Candidate Ranking
- Export Top 100 CSV
"""
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload Job Description (.txt)",
    type=["txt"],
)

col1, col2, col3 = st.columns(3)

with col1:
    run_button = st.button(
        "🚀 Run Ranking Pipeline",
        use_container_width=True,
    )

with col2:
    st.metric(
        "Dataset",
        "100,000 Candidates",
    )

with col3:
    st.metric(
        "Pipeline",
        "LangGraph",
    )

st.divider()

if run_button:

    if uploaded_file is None:

        st.error(
            "Please upload a Job Description (.txt) file."
        )

    else:

        job_path = Path("data/raw/job_description.txt")

        with open(job_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        progress = st.progress(0)

        status = st.empty()

        start = time.time()

        status.info("Reading Job Description...")
        progress.progress(10)

        status.info("Running Candidate Ranking Pipeline...")
        progress.progress(30)

        results = run_pipeline()

        status.info("Ranking Candidates...")
        progress.progress(75)

        top100 = rank_candidates(results)

        export_csv(top100)

        progress.progress(100)

        elapsed = time.time() - start

        status.success("Ranking Complete!")

        st.success(
            f"Completed in {elapsed:.2f} seconds."
        )

        st.divider()

        st.subheader("Pipeline Statistics")

        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric(
                "Candidates Processed",
                len(results),
            )

        with s2:
            st.metric(
                "Top Candidates",
                len(top100),
            )

        with s3:
            st.metric(
                "Execution Time",
                f"{elapsed:.1f}s",
            )

        st.divider()

        st.subheader("Top 100 Candidates")

        df = pd.read_csv(OUTPUT_CSV)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="📥 Download Top 100 CSV",
            data=OUTPUT_CSV.read_bytes(),
            file_name="top_100_candidates.csv",
            mime="text/csv",
        )

        st.divider()

        st.subheader("Top 10 Preview")

        st.table(df.head(10))