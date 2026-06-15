from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from app.excel_summary import summarize_excel_file
from app.ai_summary import generate_ai_summary

app = FastAPI(title="AI Excel Summary Backend")


@app.get("/")
def root():
    return {
        "message": "AI Excel Summary Backend is running."
    }


@app.get("/ui", response_class=HTMLResponse)
def upload_ui():
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
        const form = document.getElementById("upload-form");
        const fileInput = document.getElementById("file-input");
        const statusBox = document.getElementById("status");
        const submitButton = document.getElementById("submit-button");
        const resultBox = document.getElementById("result");
        const aiSummary = document.getElementById("ai-summary");
        const overviewTable = document.getElementById("overview-table");
        const rawSummary = document.getElementById("raw-summary");

        function setStatus(message, isError = false) {
            statusBox.textContent = message;
            statusBox.className = isError ? "status error" : "status";
        }

        function renderOverview(data) {
            const sheets = data.structured_summary.sheets || [];
            const rows = [
                ["Filename", data.filename],
                ["File type", data.structured_summary.file_type],
                ["Sheets", sheets.length]
            ];

            sheets.forEach((sheet, index) => {
                rows.push([`Sheet ${index + 1}`, sheet.sheet_name]);
                rows.push([`Rows in ${sheet.sheet_name}`, sheet.row_count]);
                rows.push([`Columns in ${sheet.sheet_name}`, sheet.column_count]);
                rows.push([`Column names in ${sheet.sheet_name}`, sheet.columns.join(", ")]);
            });

            overviewTable.innerHTML = rows
                .map(([label, value]) => `<tr><th>${label}</th><td>${value}</td></tr>`)
                .join("");
        }

        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const file = fileInput.files[0];
            if (!file) {
                setStatus("Please choose a CSV or Excel file first.", true);
                return;
            }

            const formData = new FormData();
            formData.append("file", file);

            submitButton.disabled = true;
            resultBox.style.display = "none";
            setStatus("Uploading and analyzing...");

            try {
                const response = await fetch("/summary", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "Upload failed.");
                }

                aiSummary.textContent = data.ai_summary.plain_english_summary || "No AI summary returned.";
                renderOverview(data);
                rawSummary.textContent = JSON.stringify(data.structured_summary, null, 2);
                resultBox.style.display = "block";
                setStatus("Done.");
            } catch (error) {
                setStatus(error.message, true);
            } finally {
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
        file_content = await file.read()

        structured_summary = summarize_excel_file(
            file_content=file_content,
            filename=file.filename
        )

        ai_summary = generate_ai_summary(structured_summary)

        return {
            "filename": file.filename,
            "structured_summary": structured_summary,
            "ai_summary": ai_summary
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
