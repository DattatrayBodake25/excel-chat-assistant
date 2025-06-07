#importing all required libraries here
import streamlit as st
import pandas as pd
import os
import google.generativeai as genai


#Importing internal modules from other files here
from utils import prepare_data, check_column_types
from user_interface import sidebar_user_interface, user_query, display_response_and_chart
from gemini_api import prepare_gemini, talk_with_gemini
from chart import getting_chart_information


# Basic setup for streamlit app
st.set_page_config(page_title="Excel ChatBot", layout="wide")
st.title("📊DataGuide: Talk to Your Excel Data")


# Sidebar User interface includes upload file, preview uploaded dataset, clean columns, types
df_clean = sidebar_user_interface()

if df_clean is not None:
    #integrating gemini model api key
    prepare_gemini(api_key=os.getenv("GEMINI_API_KEY"))

    # Ask user query and get input here
    user_query = user_query()

    if user_query:
        # Get answer from Gemini API
        answer = talk_with_gemini(user_query, df_clean)

        # get answer for text and chart info
        final_answer, chart = getting_chart_information(answer)

        # displaying answer and optional chart
        display_response_and_chart(final_answer, chart, df_clean)