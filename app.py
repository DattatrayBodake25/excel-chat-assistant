import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import plotly.express as px
from utils import preprocess_dataframe, detect_column_types

# Simple in-memory cache for Gemini Q&A results
# Cache key: (question, dataframe_hash)
qa_cache = {}

def dataframe_hash(df: pd.DataFrame) -> int:
    # Quick hash based on shape + column names + first few rows (to detect changes)
    preview_str = str(df.shape) + str(list(df.columns)) + df.head(5).to_csv()
    return hash(preview_str)

# -----------------------------
# Streamlit App Configuration
# -----------------------------
st.set_page_config(page_title="Excel Chat Assistant", layout="wide")
st.title("📊 InsightMate - Excel Chat Assistant")

# -----------------------------
# Sidebar: File Upload + Data Preview + Cleaned Columns
# -----------------------------
with st.sidebar:
    st.header("Upload & Data Info")
    uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["xlsx", "csv"])

    df = None
    if uploaded_file is not None:
        with st.spinner("Uploading and reading file..."):
            try:
                if uploaded_file.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    st.warning("Unsupported file type.")

                if df is not None:
                    st.success("✅ File uploaded and read successfully!")
                    st.subheader("📄 Data Preview")
                    st.dataframe(df.head(20))

            except Exception as e:
                st.error(f"❌ Error reading the file: {e}")
    else:
        st.info("📁 Please upload a .xlsx or .csv file to begin.")

    if df is not None:
        df_clean = preprocess_dataframe(df)
        st.subheader("🧹 Cleaned Column Names")
        st.write(df_clean.columns.tolist())
    else:
        df_clean = None

# -----------------------------
# Main Content Area: Detected Types + Q&A + Chart
# -----------------------------
if df_clean is not None:
    types = detect_column_types(df_clean)
    st.subheader("🔍 Detected Column Types")
    st.json(types)

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def ask_gemini(question: str, df: pd.DataFrame) -> str:
        """Ask Gemini for answer and chart instructions, with caching"""
        key = (question, dataframe_hash(df))
        if key in qa_cache:
            return qa_cache[key]

        column_info = "\n".join([f"- {col}: {dtype}" for col, dtype in zip(df.columns, df.dtypes)])
        sample_rows = df.head(500).to_dict(orient="records")

        prompt = f"""
You are an assistant that analyzes spreadsheet data.

Sample data:
{sample_rows}

Column details:
{column_info}

User asked:
"{question}"

1. Provide a brief answer in plain English.
2. If a chart is helpful, respond with this exact format:

CHART: bar|line|hist|scatter
X: column_name
Y: column_name

Only include the CHART section if needed. Do NOT use markdown or explanations.
"""

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        qa_cache[key] = response.text
        return response.text

    def parse_chart_instruction(response: str):
        """Extract chart metadata if available"""
        lines = response.strip().splitlines()
        chart_info = {"type": None, "x": None, "y": None}
        chart_start_index = None
        for i, line in enumerate(lines):
            if line.startswith("CHART:"):
                chart_start_index = i
                chart_info["type"] = line.split(":")[1].strip().lower()
                if i + 1 < len(lines) and lines[i + 1].startswith("X:"):
                    chart_info["x"] = lines[i + 1].split(":", 1)[1].strip()
                if i + 2 < len(lines) and lines[i + 2].startswith("Y:"):
                    chart_info["y"] = lines[i + 2].split(":", 1)[1].strip()
                break
        if chart_start_index is not None:
            answer_text = "\n".join(lines[:chart_start_index])
        else:
            answer_text = response
        return answer_text, chart_info

    st.subheader("💬 Ask a Question About the Data")
    user_query = st.text_input("")

    if user_query:
        with st.spinner("Thinking..."):
            answer = ask_gemini(user_query, df_clean)

        final_answer, chart = parse_chart_instruction(answer)
        st.subheader("🤖 Gemini's Response")
        st.markdown(final_answer)

        if chart["type"]:
            st.subheader("📈 Visual Insight")

            # Allow manual override of chart type
            chart_types = ["bar", "line", "hist", "scatter"]
            selected_chart_type = st.selectbox("Select chart type (override AI suggestion):", 
                                               options=["Auto (AI suggestion)"] + chart_types, 
                                               index=0)
            chart_type = chart["type"] if selected_chart_type == "Auto (AI suggestion)" else selected_chart_type

            # Warn if data too large for plotting
            max_rows_for_plot = 5000
            if len(df_clean) > max_rows_for_plot:
                st.warning(f"⚠️ Data has {len(df_clean)} rows; plotting may be slow or unresponsive. Showing first {max_rows_for_plot} rows instead.")
                plot_df = df_clean.head(max_rows_for_plot)
            else:
                plot_df = df_clean

            try:
                # Validate columns
                if chart["x"] not in plot_df.columns:
                    st.warning(f"⚠️ Column '{chart['x']}' not found in data.")
                elif chart_type != "hist" and chart["y"] not in plot_df.columns:
                    st.warning(f"⚠️ Column '{chart['y']}' not found in data.")
                else:
                    fig = None
                    if chart_type == "bar":
                        fig = px.bar(plot_df, x=chart["x"], y=chart["y"])
                    elif chart_type == "line":
                        fig = px.line(plot_df, x=chart["x"], y=chart["y"])
                    elif chart_type == "hist":
                        fig = px.histogram(plot_df, x=chart["x"])
                    elif chart_type == "scatter":
                        fig = px.scatter(plot_df, x=chart["x"], y=chart["y"])
                    else:
                        st.warning("⚠️ Unknown chart type")

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"📉 Chart error: {e}")