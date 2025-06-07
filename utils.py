import pandas as pd
import re

def normalize_column_name(col: str) -> str:
    """
    Normalize a column name:
    - Lowercase
    - Remove special characters
    - Replace spaces with underscores
    """
    col = col.strip().lower()
    col = re.sub(r"[^\w\s]", "", col)      # Remove special characters
    col = re.sub(r"\s+", "_", col)         # Replace spaces with underscores
    return col

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names across the DataFrame.
    """
    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    return df

def detect_column_types(df: pd.DataFrame) -> dict:
    """
    Detect column types: numerical, categorical, boolean, datetime.
    - Applies parsing to identify datetime columns even if they are stored as strings.
    """
    types = {
        "numerical": [],
        "categorical": [],
        "boolean": [],
        "datetime": []
    }

    for col in df.columns:
        col_data = df[col].dropna()

        # Boolean detection
        if pd.api.types.is_bool_dtype(col_data):
            types["boolean"].append(col)
            continue

        # Numeric detection
        if pd.api.types.is_numeric_dtype(col_data):
            types["numerical"].append(col)
            continue

        # Datetime detection with parsing
        try:
            parsed_dates = pd.to_datetime(col_data, errors="coerce", dayfirst=False)
            valid_count = parsed_dates.notna().sum()
            if valid_count / len(col_data) > 0.7:
                types["datetime"].append(col)
                continue
        except Exception:
            pass

        # Fallback: Categorical
        types["categorical"].append(col)

    return types