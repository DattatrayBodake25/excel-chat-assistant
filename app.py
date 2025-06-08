#importing all required libraries
import streamlit as st
import os
# Import internal modules
from utils import data_preparing, column_types_checking
from user_interface import user_interface_sidebar, user_question, show_response_and_chart
from gemini_api import gemini_setup, chat_with_gemini
from chart import getting_chart_information

# Streamlit app setup
st.set_page_config(page_title="Excel ChatBot", layout="wide")
st.title("📊 DataGuide: Talk to Your Excel Data")

# Sidebar for uploading and cleaning data
df_clean = user_interface_sidebar()

if df_clean is not None:
    # Initialize Gemini API
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error("GEMINI_API_KEY environment variable not set.")
    else:
        gemini_setup(api_key=gemini_api_key)

        # Get user question input
        question = user_question()

        if question:
            # Get answer and chart info from Gemini
            answer = chat_with_gemini(question, df_clean)
            final_answer, chart = getting_chart_information(answer)

            # Display results and visualizations
            show_response_and_chart(final_answer, chart, df_clean)