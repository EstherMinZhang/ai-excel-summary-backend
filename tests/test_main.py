from fastapi.testclient import TestClient  # FastAPI 提供的测试客户端，用来模拟浏览器/API 请求
from app.main import app  # 导入 main.py 中创建的 FastAPI 应用

client = TestClient(app)  # 创建测试客户端，后面可以用 client.get/client.post 调接口


def test_root_endpoint():
    # 调用 GET / 根路径接口
    response = client.get("/")

    # 断言 HTTP 状态码是 200，表示请求成功
    assert response.status_code == 200
    # 断言返回的 JSON 里包含预期 message
    assert response.json()["message"] == "AI Excel Summary Backend is running."


def test_upload_ui_page():
    # 调用 GET /ui，获取上传页面 HTML
    response = client.get("/ui")

    # 检查页面请求成功
    assert response.status_code == 200
    # 检查 HTML 中有页面标题
    assert "AI Excel Summary" in response.text
    # 检查 HTML 中有文件上传输入框
    assert 'type="file"' in response.text
    # 检查 HTML 中有提交按钮文字
    assert "Analyze file" in response.text


# 测试上传 CSV 文件到 /summary 接口
#test
def test_summary_endpoint_with_csv(monkeypatch):
    # 定义假的 AI 总结函数，避免测试时真的调用 Gemini API
    def fake_ai_summary(structured_summary):
        return {
            "plain_english_summary": "Fake AI summary for testing."
        }

    # monkeypatch 会临时替换 app.main.generate_ai_summary
    # 这样接口内部调用 generate_ai_summary 时，会调用上面的假函数
    monkeypatch.setattr("app.main.generate_ai_summary", fake_ai_summary)

    # b"..." 表示 bytes（二进制数据），模拟一个用户上传的 CSV 文件内容
    csv_content = b"Name,Age,City\nAlice,25,Vancouver\nBob,30,Toronto\n"

    # 发送 POST /summary 请求，并用 files 参数模拟文件上传
    response = client.post(
        "/summary",
        files={
            # 格式是：(文件名, 文件内容, 文件 MIME 类型)
            "file": ("test.csv", csv_content, "text/csv")
        }
    )

    # 检查接口返回成功
    assert response.status_code == 200
    # response.json() 把响应 JSON 转成 Python 字典
    data = response.json()

    # 下面这些断言检查后端解析 CSV 后的结果是否正确
    assert data["filename"] == "test.csv"
    assert data["structured_summary"]["file_type"] == "csv"
    assert data["structured_summary"]["sheets"][0]["row_count"] == 2
    assert data["structured_summary"]["sheets"][0]["column_count"] == 3
    assert data["ai_summary"]["plain_english_summary"] == "Fake AI summary for testing."


from io import BytesIO  # BytesIO 用来在内存中创建一个“像文件一样”的对象
import pandas as pd  # pandas 用于创建测试用的表格数据


# 测试上传 Excel 文件到 /summary 接口
def test_summary_endpoint_with_excel(monkeypatch):
    # 定义假的 AI 总结函数，避免测试时真的调用 Gemini API
    def fake_ai_summary(structured_summary):
        return {
            "plain_english_summary": "Fake AI summary for Excel testing."
        }

    # 临时替换真正的 AI 函数
    monkeypatch.setattr("app.main.generate_ai_summary", fake_ai_summary)

    # 创建一个内存文件，用来保存测试 Excel 内容
    excel_file = BytesIO()

    # 创建一个 DataFrame，类似一张有三列两行的表格
    df = pd.DataFrame({
        "Name": ["Alice", "Bob"],
        "Age": [25, 30],
        "City": ["Vancouver", "Toronto"]
    })

    # ExcelWriter 把 DataFrame 写入内存中的 Excel 文件
    # with 会在代码块结束后自动关闭 writer
    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        # index=False 表示不要把 DataFrame 的行号写进 Excel
        df.to_excel(writer, sheet_name="People", index=False)

    # 把内存文件的读取位置移回开头，否则后面读取可能读不到内容
    excel_file.seek(0)

    # 发送 POST /summary 请求，模拟上传 Excel 文件
    response = client.post(
        "/summary",
        files={
            "file": (
                "test.xlsx",
                excel_file.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        }
    )

    # 检查接口返回成功
    assert response.status_code == 200
    # 把响应 JSON 转成 Python 字典
    data = response.json()

    # 下面这些断言检查后端解析 Excel 后的结果是否正确
    assert data["filename"] == "test.xlsx"
    assert data["structured_summary"]["file_type"] == "excel"
    assert data["structured_summary"]["sheets"][0]["sheet_name"] == "People"
    assert data["structured_summary"]["sheets"][0]["row_count"] == 2
    assert data["structured_summary"]["sheets"][0]["column_count"] == 3
    assert data["ai_summary"]["plain_english_summary"] == "Fake AI summary for Excel testing."


# 测试上传不支持的文件类型时，接口是否返回 400 错误
def test_summary_endpoint_with_invalid_file_type():
    # 准备一个 txt 文件内容，后端不支持这个类型
    txt_content = b"This is not a CSV or Excel file."

    # 发送 POST /summary 请求，模拟上传 txt 文件
    response = client.post(
        "/summary",
        files={
            "file": ("test.txt", txt_content, "text/plain")
        }
    )

    # 检查状态码是 400，表示用户输入/文件类型有问题
    assert response.status_code == 400
    # 检查错误信息是否符合预期
    assert response.json()["detail"] == "Unsupported file type. Please upload a CSV or Excel file."
