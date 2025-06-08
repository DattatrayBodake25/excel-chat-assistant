# Excel-Assistant

## Overview
This is a Streamlit-based chatbot that allows users to upload Excel or CSV files, ask natural language questions about the data, and receive insights along with dynamic visualizations. The app uses the Gemini LLM API to understand and analyze datasets of varying schemas.

## Features
- Upload Excel (.xlsx) or CSV files
- Automatic data cleaning and type inference
- Natural language querying powered by Gemini LLM
- Intelligent chart suggestions including bar, line, histogram, scatter, pie, and box plots
- Option to override chart type and columns
- Displays Gemini’s interpretation of data schema for transparency
- User-friendly interface with real-time response and visualizations

## Setup Instructions
1. Clone the repo:
```
git clone https://github.com/DattatrayBodake25/excel-chat-assistant
```
2. Install dependencies:
```
pip install -r requirements.txt
```
4. Set your Gemini API key as an environment variable:
- Linux/macOS:
  ```
  export GEMINI_API_KEY="your_api_key_here"
  ```
- Windows:
  ```
  set GEMINI_API_KEY="your_api_key_here"
  ```
4. Run the Streamlit app:
```
streamlit run app.py
```

## Usage
- Upload your Excel or CSV file in the sidebar.
- Preview and verify the cleaned data.
- View the inferred column types.
- Type your question in natural language.
- Get insights and suggested charts with the option to customize visualizations.

## Notes
- Supports datasets with a wide range of column schemas.
- Chart suggestions are based on Gemini’s interpretation but can be overridden.
- API usage may have rate limits depending on your Gemini plan.

## Credits
- Built using Streamlit, Pandas, Plotly, and Google Gemini LLM API.
---

