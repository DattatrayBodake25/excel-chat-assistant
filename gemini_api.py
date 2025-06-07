#importing all required libraries here
import os
import google.generativeai as genai
from typing import Tuple
import pandas as pd


# simple In-memory cache for gemini question and answer 
user_query_cache = {}


#initializing the gemini api key and model
def prepare_gemini(api_key: str):
    genai.configure(api_key=api_key)


#identify dataset
def identify_dataframe(df: pd.DataFrame) -> int:
    preview_string = str(df.shape) + str(list(df.columns)) + df.head(5).to_csv()
    return hash(preview_string)


#question and answering with gemini model
def talk_with_gemini(question: str, df: pd.DataFrame) -> str:
    key = (question, identify_dataframe(df))
    if key in user_query_cache:
        return user_query_cache[key]

    column_information = "\n".join([f"- {column}: {dtype}" for column, dtype in zip(df.columns, df.dtypes)])
    sample_rows = df.head(500).to_dict(orient="records")

    #writing prompt template here
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
    
    #generate the response to user query using gemini flash model
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    user_query_cache[key] = response.text
    return response.text