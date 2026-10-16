from fastapi import FastAPI, UploadFile, File, HTTPException  # 引入 FastAPI 核心组件
from fastapi.responses import HTMLResponse  # 引入 HTMLResponse，用于返回 HTML 页面
from app.excel_summary import summarize_excel_file  # 导入处理 Excel/CSV 的函数
from app.ai_summary import generate_ai_summary  # 导入调用 Gemini AI 的函数

app = FastAPI(title="AI Excel Summary Backend")  # 创建 FastAPI 应用实例


@app.get("/")
def root():
    # 根路径接口，返回服务运行状态
    return {
        "message": "AI Excel Summary Backend is running."
    }


@app.get("/ui", response_class=HTMLResponse)
def upload_ui():
    # 返回一个简单的前端上传页面，这里写在后端代码里
    # 三个引号 """...""" 表示多行字符串，可以直接保存整段 HTML
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Excel Summary</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            color: #1f2937;
        }

        main {
            max-width: 880px;
            margin: 48px auto;
            padding: 0 20px;
        }

        h1 {
            margin-bottom: 8px;
            font-size: 32px;
        }

        .subtitle {
            margin-top: 0;
            color: #5b6472;
        }

        .panel {
            margin-top: 28px;
            padding: 24px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
        }

        .upload-row {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
        }

        input[type="file"] {
            flex: 1;
            min-width: 260px;
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            background: #fff;
        }

        button {
            padding: 11px 18px;
            border: 0;
            border-radius: 6px;
            background: #2563eb;
            color: white;
            font-weight: 700;
            cursor: pointer;
        }

        button:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }

        .status {
            margin-top: 16px;
            min-height: 24px;
            color: #4b5563;
        }

        .error {
            color: #b91c1c;
        }

        .result {
            display: none;
            margin-top: 24px;
        }

        .summary-text {
            line-height: 1.6;
            white-space: pre-wrap;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 14px;
            font-size: 14px;
        }

        th, td {
            padding: 10px;
            border-bottom: 1px solid #e5e7eb;
            text-align: left;
            vertical-align: top;
        }

        th {
            background: #f8fafc;
        }

        code {
            display: block;
            max-height: 260px;
            overflow: auto;
            padding: 14px;
            border-radius: 6px;
            background: #111827;
            color: #e5e7eb;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <main>
        <h1>AI Excel Summary</h1>
        <p class="subtitle">Upload a CSV or Excel file and get a quick AI-generated summary.</p>

        <section class="panel">
            <form id="upload-form">
                <div class="upload-row">
                    <input id="file-input" name="file" type="file" accept=".csv,.xlsx,.xls" />
                    <button id="submit-button" type="submit">Analyze file</button>
                </div>
                <div id="status" class="status">Choose a file to begin.</div>
            </form>
        </section>

        <section id="result" class="panel result">
            <h2>AI Summary</h2>
            <p id="ai-summary" class="summary-text"></p>

            <h2>File Overview</h2>
            <table>
                <tbody id="overview-table"></tbody>
            </table>

            <h2>Raw Structured Summary</h2>
            <code id="raw-summary"></code>
        </section>
    </main>

    <script>
        // document.getElementById(...) 表示从页面里按 id 找到一个 HTML 元素
        const form = document.getElementById("upload-form");
        const fileInput = document.getElementById("file-input");
        const statusBox = document.getElementById("status");
        const submitButton = document.getElementById("submit-button");
        const resultBox = document.getElementById("result");
        const aiSummary = document.getElementById("ai-summary");
        const overviewTable = document.getElementById("overview-table");
        const rawSummary = document.getElementById("raw-summary");

        // 定义一个函数，用来更新页面上的状态文字
        // isError = false 表示如果调用时不传第二个参数，默认不是错误状态
        function setStatus(message, isError = false) {
            // textContent 会修改元素显示出来的文字
            statusBox.textContent = message;
            // 三元表达式：条件 ? 条件为真时的值 : 条件为假时的值
            statusBox.className = isError ? "status error" : "status";
        }

        // 定义一个函数，把后端返回的结构化摘要显示成表格
        function renderOverview(data) {
            // || [] 表示如果 sheets 不存在，就使用空数组，避免页面报错
            const sheets = data.structured_summary.sheets || [];
            // rows 是二维数组，每个小数组代表表格中的一行：[左侧标题, 右侧内容]
            const rows = [
                ["Filename", data.filename],
                ["File type", data.structured_summary.file_type],
                ["Sheets", sheets.length]
            ];

            // forEach 会遍历数组里的每一个 sheet
            sheets.forEach((sheet, index) => {
                // push(...) 表示向数组末尾添加新的一行
                rows.push([`Sheet ${index + 1}`, sheet.sheet_name]);
                rows.push([`Rows in ${sheet.sheet_name}`, sheet.row_count]);
                rows.push([`Columns in ${sheet.sheet_name}`, sheet.column_count]);
                rows.push([`Column names in ${sheet.sheet_name}`, sheet.columns.join(", ")]);
            });

            // map(...) 把每一行数据转换成 HTML 字符串，join("") 再拼成完整表格内容
            overviewTable.innerHTML = rows
                .map(([label, value]) => `<tr><th>${label}</th><td>${value}</td></tr>`)
                .join("");
        }

        // 监听表单提交事件；async 表示这个函数里可以使用 await 等待网络请求
        form.addEventListener("submit", async (event) => {
            // 阻止浏览器默认提交表单并刷新页面
            event.preventDefault();
            // 取用户选择的第一个文件
            const file = fileInput.files[0];
            if (!file) {
                // 如果用户还没有选文件，就显示错误并结束函数
                setStatus("Please choose a CSV or Excel file first.", true);
                return;
            }
            // FormData 用于模拟浏览器上传文件的表单数据
            const formData = new FormData();
            // "file" 必须和后端 summarize_file(file: UploadFile = File(...)) 的参数名一致
            formData.append("file", file);
            // 上传期间禁用按钮，避免用户重复点击
            submitButton.disabled = true;
            resultBox.style.display = "none";
            setStatus("Uploading and analyzing...");
            try {
                // fetch(...) 向后端 /summary 接口发送 POST 请求
                // await 表示等待后端响应后，再继续执行下面的代码
                const response = await fetch("/summary", {
                    method: "POST",
                    body: formData
                });
                // 把后端返回的 JSON 文本解析成 JavaScript 对象
                const data = await response.json();
                if (!response.ok) {
                    // throw 会跳到下面的 catch，由 catch 统一显示错误
                    throw new Error(data.detail || "Upload failed.");
                }
                // 显示 AI 总结；如果没有返回内容，就显示默认提示
                aiSummary.textContent = data.ai_summary.plain_english_summary || "No AI summary returned.";
                // 显示文件概览表格
                renderOverview(data);
                // JSON.stringify(..., null, 2) 把对象格式化成缩进为 2 个空格的 JSON 文本
                rawSummary.textContent = JSON.stringify(data.structured_summary, null, 2);
                // 分析成功后显示结果区域
                resultBox.style.display = "block";
                setStatus("Done.");
            } catch (error) {
                // 网络错误、后端错误或 throw 出来的错误都会在这里处理
                setStatus(error.message, true);
            } finally {
                // finally 无论成功还是失败都会执行，用来恢复按钮可点击状态
                submitButton.disabled = false;
            }
        });
    </script>
</body>
</html>
"""


@app.post("/summary")
async def summarize_file(file: UploadFile = File(...)):
    try:
        # 读取上传文件的二进制内容
        file_content = await file.read()

        # 解析文件，生成结构化摘要数据
        structured_summary = summarize_excel_file(
            file_content=file_content,
            filename=file.filename
        )

        # 调用 AI 生成自然语言总结
        ai_summary = generate_ai_summary(structured_summary)

        # 返回文件名、结构化摘要和 AI 总结
        return {
            "filename": file.filename,
            "structured_summary": structured_summary,
            "ai_summary": ai_summary
        }

    except ValueError as e:
        # 如果文件类型不支持，返回 400 错误
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # 其他异常返回 500 错误
        raise HTTPException(status_code=500, detail=str(e))
