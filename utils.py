#importing here all required libraries 
from typing import Dict
import pandas as pd
import re


#writing function here for the process column names and normalizing columns
def processing_columns(column: str) -> str:
    """
    Clean and normalize a single column name.
    1. convert all characters in lowercase 2.special characters removing 3.underscores inplace of spaces
    """
    column = column.strip().lower()
    column = re.sub(r"[^\w\s]", "", column)
    column = re.sub(r"\s+", "_", column)
    return column


#writing function for the data preparing for analysis
def data_preparing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleaning column names, converts datatypes, and fills missing values.
    """
    df = df.copy()
    df.columns = [processing_columns(column) for column in df.columns]

    for column in df.columns:
        #here trying to convert in numerical format
        numeric_column = pd.to_numeric(df[column], errors='coerce')
        if numeric_column.notna().sum() > (len(df) / 2):
            df[column] = numeric_column
            df[column].fillna(df[column].median(), inplace=True)
            continue

        #here trying to convert in datetime format
        datetime_column = pd.to_datetime(df[column], errors='coerce', dayfirst=False)
        if datetime_column.notna().sum() > (len(df) / 2):
            df[column] = datetime_column
            df[column].fillna(method='ffill', inplace=True)
            continue

        #trying to convert in boolean type
        boolean_like = df[column].astype(str).str.lower().isin(["true", "false", "yes", "no", "1", "0"])
        if boolean_like.sum() > (len(df) / 2):
            df[column] = df[column].astype(str).str.lower().map({
                "true": True, "yes": True, "1": True,
                "false": False, "no": False, "0": False
            })
            df[column].fillna(False, inplace=True)
            continue

        # null values in Categorical column  handling
        df[column] = df[column].astype(str).fillna("Unknown")

    return df


#writing function here to check column types automatically
def column_types_checking(df: pd.DataFrame) -> Dict[str, list]:
    """
    Identifying data types for each column:
    """
    types_of_column = {
        "numerical_type": [],
        "categorical_type": [],
        "boolean_type": [],
        "datetime_type": []
    }
    
    for column in df.columns:
        column_data = df[column].dropna()

        if pd.api.types.is_bool_dtype(column_data):
            types_of_column["boolean_type"].append(column)
        elif pd.api.types.is_numeric_dtype(column_data):
            types_of_column["numerical_type"].append(column)
        elif pd.api.types.is_datetime64_any_dtype(column_data):
            types_of_column["datetime_type"].append(column)
        else:
            types_of_column["categorical_type"].append(column)

    return types_of_column