#importing all required libraries here
import google.generativeai as genai
from typing import Tuple
import pandas as pd
import os


# In-memory cache to avoid repeated calls for same input
user_query_cache = {}


#writing function here for gemini api key set up.
def gemini_setup(api_key: str):
    """
    Set up the Gemini API here using the key.
    """
    genai.configure(api_key=api_key)


#writing function here for dataframe
def identify_dataframe(df: pd.DataFrame) -> int:
    """
    create a unique hash based on shape, column names, and preview content.
    """
    check_string = str(df.shape) + str(list(df.columns)) + df.head(5).to_csv(index=False)
    return hash(check_string)


#writing function here for chat with gemini model
def chat_with_gemini(question: str, df: pd.DataFrame) -> str:
    key = (question, identify_dataframe(df))
    if key in user_query_cache:
        return user_query_cache[key]

    sample_df = df.head(500)
    sample_records = sample_df.to_dict(orient="records")

    column_information = []
    for column in df.columns:
        dtype = df[column].dtype
        unique_values = df[column].nunique(dropna=True)
        example_values = sample_df[column].dropna().unique()[:3]
        column_summary = f"- {column} ({dtype}, {unique_values} unique): e.g. {list(example_values)}"
        column_information.append(column_summary)

    column_description = "\n".join(column_information)
    

    prompt = f"""
You are a data assistant that analyzes Excel/CSV datasets and answers user questions.

=== DATA OVERVIEW ===
Sample data (first 10 rows):
{sample_records}

Column descriptions:
{column_description}

=== USER QUESTION ===
"{question}"

=== INSTRUCTIONS ===
1. Answer briefly in plain English.
2. If a chart helps, reply in **this exact format**:

CHART: bar|line|hist|scatter
X: column_name
Y: column_name

Only include the CHART section if needed. Do NOT include markdown, explanations, or extra lines.
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        if not response.text or response.text.strip() == "":
            raise ValueError("Empty response from Gemini.")

        user_query_cache[key] = response.text
        return response.text

    except Exception as e:
        return f"I'm sorry, I couldn't understand that question. Please try rephrasing it. (Error: {e})"