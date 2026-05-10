import pandas as pd
from io import BytesIO


def summarize_excel_file(file_content: bytes, filename: str) -> dict:
    file_stream = BytesIO(file_content)

    if filename.endswith(".csv"):
        df = pd.read_csv(file_stream)
        return {
            "file_type": "csv",
            "sheets": [
                summarize_dataframe(df, "CSV File")
            ]
        }

    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        excel_file = pd.ExcelFile(file_stream)
        sheets = []

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            sheets.append(summarize_dataframe(df, sheet_name))

        return {
            "file_type": "excel",
            "sheets": sheets
        }

    raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")


def summarize_dataframe(df: pd.DataFrame, sheet_name: str) -> dict:
    return {
        "sheet_name": sheet_name,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict()
    }