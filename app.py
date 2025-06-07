#importing required libraries here
import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import plotly.express as px
from utils import prepare_data, check_column_types

# Simple in-memory cache for Gemini model Question and answer results
user_query_cache = {}

def identify_dataframe(df: pd.DataFrame) -> int:
    # Quickly generates a hash using size, columns, and sample rows to check if the data has changed
    preview_string = str(df.shape) + str(list(df.columns)) + df.head(5).to_csv()
    return hash(preview_string)

# Basic setup for how the app looks and its title
st.set_page_config(page_title="Excel ChatBot", layout="wide")
st.title("📊DataGuide: Talk to Your Excel Data")

#Adding Streamlit Sidebar including file uploading, data preview, cleaned columns, and detected types
with st.sidebar:
    st.header("Upload Your File & Check Data")
    uploaded_file = st.file_uploader("Upload here your Excel or CSV file", type=["xlsx", "csv"])

    df = None
    if uploaded_file is not None:
        with st.spinner("Uploading and reading file..."):
            try:
                if uploaded_file.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    st.warning("Please use a file that’s Excel or CSV only.")

                if df is not None:
                    st.success("Your Data uploaded and loaded Successfully!")
                    st.subheader("Preview Data")
                    st.dataframe(df.head(20))

            except Exception as e:
                st.error(f"Error reading the file: {e}")
    else:
        st.info("Please upload only a .xlsx or .csv file to start.")

    if df is not None:
        df_clean = prepare_data(df)
        st.subheader("Simplified Column Headers:")
        st.write(df_clean.columns.tolist())

        #classifing the column types here
        types = check_column_types(df_clean)
        st.subheader("Auto Classified Column Types")
        st.json(types)
    else:
        df_clean = None

# creating Main part for asking questions and checking visualization
if df_clean is not None:
    #here I have used google gemini api key for gemini llm model from .env file
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def talk_with_gemini(question: str, df: pd.DataFrame) -> str:
        key = (question, identify_dataframe(df))
        if key in user_query_cache:
            return user_query_cache[key]

        column_information = "\n".join([f"- {column}: {dtype}" for column, dtype in zip(df.columns, df.dtypes)])
        sample_rows = df.head(500).to_dict(orient="records")

        prompt = f"""
You are an assistant that analyzes excel/csv/spreadsheet data.

Sample data:
{sample_rows}

Column details:
{column_information}

User asked:
"{question}"

1. Provide a brief answer in plain and simple English.
2. If a chart is helpful, respond with this exact format:

CHART: bar|line|hist|scatter
X: column_name
Y: column_name

Only include the CHART section if needed. Do NOT use markdown or explanations.
"""
        #here i have used gemini-flash model
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        user_query_cache[key] = response.text
        return response.text

    def get_chart_information(response: str):
        lines = response.strip().splitlines()
        chart_information = {"type": None, "x": None, "y": None}
    
        for i, line in enumerate(lines):
            if line.startswith("CHART:"):
                chart_information["type"] = line.split(":", 1)[1].strip().lower()
                chart_information["x"] = lines[i + 1].split(":", 1)[1].strip() if i + 1 < len(lines) else None
                chart_information["y"] = lines[i + 2].split(":", 1)[1].strip() if i + 2 < len(lines) else None
                return "\n".join(lines[:i]), chart_information

        return response, chart_information


    st.subheader("🤔 Ask anything about your data")
    user_query = st.text_input("")

    if user_query:
        with st.spinner("Thinking..."):
            answer = talk_with_gemini(user_query, df_clean)

        final_answer, chart = get_chart_information(answer)
        st.subheader("✨ Answer from Gemini")
        st.markdown(final_answer)

        if chart["type"]:
            st.subheader("📈 Chart Insight")

            # Allowing manual override of chart type
            chart_types = ["bar", "line", "hist", "scatter"]
            choose_chart_type = st.selectbox("Select chart type (override AI suggestion):", 
                                               options=["Auto (AI suggestion)"] + chart_types, 
                                               index=0)
            chart_type = chart["type"] if choose_chart_type == "Auto (AI suggestion)" else choose_chart_type

            # Warning here if data is too large for plotting
            max_rows_for_plot = 5000
            if len(df_clean) > max_rows_for_plot:
                st.warning(f"Data has {len(df_clean)} rows; plotting may be slow or unresponsive. Showing first {max_rows_for_plot} rows instead.")
                plot_df = df_clean.head(max_rows_for_plot)
            else:
                plot_df = df_clean

            try:
                # Validating columns here
                if chart["x"] not in plot_df.columns:
                    st.warning(f"Column '{chart['x']}' not found in data.")
                elif chart_type != "hist" and chart["y"] not in plot_df.columns:
                    st.warning(f"Column '{chart['y']}' not found in data.")
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
                        st.warning("Unknown chart type")

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Chart error: {e}")