#here importing all required libraries
import pandas as pd
import re


#writing here function to process column names
def clean_column_name(column: str) -> str:
    #lowercasing column names
    column = column.strip().lower()

    #removing special characters
    column = re.sub(r"[^\w\s]", "", column)

    #replacing spaces with underscores
    column = re.sub(r"\s+", "_", column)
    
    #return clean column names
    return column


#writing function to prepare dataset here
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [clean_column_name(column) for column in df.columns]
    return df


#writing function to check column types
def check_column_types(df: pd.DataFrame) -> dict:
    #Detecting column types: numerical, categorical, boolean, datetime.
    types = {
        "numerical": [],
        "categorical": [],
        "boolean": [],
        "datetime": []
    }

    for column in df.columns:
        column_data = df[column].dropna()

        # Boolean data type detection
        if pd.api.types.is_bool_dtype(column_data):
            types["boolean"].append(column)
            continue

        # Numerical datatype detection
        if pd.api.types.is_numeric_dtype(column_data):
            types["numerical"].append(column)
            continue

        # Datetime detection with parsing
        try:
            parsed_dates = pd.to_datetime(column_data, errors="coerce", dayfirst=False)
            valid_count = parsed_dates.notna().sum()
            if valid_count / len(column_data) > 0.7:
                types["datetime"].append(column)
                continue
        except Exception:
            pass

        #Categorical columns
        types["categorical"].append(column)

    #return types of columns
    return types