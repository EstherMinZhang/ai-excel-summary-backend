import pandas as pd  # 引入 pandas 库，并简写为 pd，用于读取和处理表格数据
from io import BytesIO  # 从 io 模块引入 BytesIO，用于把二进制数据当成文件对象处理


def summarize_excel_file(file_content: bytes, filename: str) -> dict:
    # 1. 将上传的文件二进制数据包装成一个内存文件对象
    file_stream = BytesIO(file_content)

    # 2. 如果文件名以 .csv 结尾，说明这是一个 CSV 文件
    if filename.endswith(".csv"):
        # 用 pandas 读取 CSV 内容，生成 DataFrame（类似表格的数据结构）
        df = pd.read_csv(file_stream)
        return {
            "file_type": "csv",  # 标记文件类型为 csv
            "sheets": [
                summarize_dataframe(df, "CSV File")  # 处理单个 CSV 表格，生成结构化摘要
            ]
        }

    # 3. 如果文件名以 .xlsx 或 .xls 结尾，说明这是一个 Excel 文件
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        # 用 pandas 解析 Excel 文件，得到一个 ExcelFile 对象
        excel_file = pd.ExcelFile(file_stream)
        sheets = []  # 存放每个 sheet 的摘要结果

        # 遍历 Excel 文件中的每个 sheet 名称
        for sheet_name in excel_file.sheet_names:
            # 读取当前 sheet 内容，生成 DataFrame
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # 将当前 sheet 的结构化摘要追加到 sheets 列表
            sheets.append(summarize_dataframe(df, sheet_name))

        return {
            "file_type": "excel",  # 标记文件类型为 excel
            "sheets": sheets  # 包含所有 sheet 的摘要列表
        }

    # 4. 如果既不是 CSV 也不是 Excel，则抛出错误
    raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")


def summarize_dataframe(df: pd.DataFrame, sheet_name: str) -> dict:
    # 生成单张表（DataFrame）的摘要信息，并返回一个字典
    return {
        "sheet_name": sheet_name,  # 当前 sheet 的名字
        "row_count": int(len(df)),  # 行数
        "column_count": int(len(df.columns)),  # 列数
        "columns": list(df.columns),  # 列名列表
        "missing_values": df.isnull().sum().to_dict(),  # 每列的缺失值数量
        "data_types": df.dtypes.astype(str).to_dict()  # 每列的数据类型
    }
