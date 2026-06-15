from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "AI Excel Summary Backend is running."


def test_upload_ui_page():
    response = client.get("/ui")

    assert response.status_code == 200
    assert "AI Excel Summary" in response.text
    assert 'type="file"' in response.text
    assert "Analyze file" in response.text

# added test for the /summary endpoint with a CSV file upload
def test_summary_endpoint_with_csv(monkeypatch):
    def fake_ai_summary(structured_summary):
        return {
            "plain_english_summary": "Fake AI summary for testing."
        }

    monkeypatch.setattr("app.main.generate_ai_summary", fake_ai_summary)

    csv_content = b"Name,Age,City\nAlice,25,Vancouver\nBob,30,Toronto\n"

    response = client.post(
        "/summary",
        files={
            "file": ("test.csv", csv_content, "text/csv")
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["filename"] == "test.csv"
    assert data["structured_summary"]["file_type"] == "csv"
    assert data["structured_summary"]["sheets"][0]["row_count"] == 2
    assert data["structured_summary"]["sheets"][0]["column_count"] == 3
    assert data["ai_summary"]["plain_english_summary"] == "Fake AI summary for testing."

# added test for the /summary endpoint with an Excel file upload
from io import BytesIO
import pandas as pd


def test_summary_endpoint_with_excel(monkeypatch):
    def fake_ai_summary(structured_summary):
        return {
            "plain_english_summary": "Fake AI summary for Excel testing."
        }

    monkeypatch.setattr("app.main.generate_ai_summary", fake_ai_summary)

    excel_file = BytesIO()

    df = pd.DataFrame({
        "Name": ["Alice", "Bob"],
        "Age": [25, 30],
        "City": ["Vancouver", "Toronto"]
    })

    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="People", index=False)

    excel_file.seek(0)

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

    assert response.status_code == 200
    data = response.json()

    assert data["filename"] == "test.xlsx"
    assert data["structured_summary"]["file_type"] == "excel"
    assert data["structured_summary"]["sheets"][0]["sheet_name"] == "People"
    assert data["structured_summary"]["sheets"][0]["row_count"] == 2
    assert data["structured_summary"]["sheets"][0]["column_count"] == 3
    assert data["ai_summary"]["plain_english_summary"] == "Fake AI summary for Excel testing."


# 4 added test for the /summary endpoint with an unsupported file type
def test_summary_endpoint_with_invalid_file_type():
    txt_content = b"This is not a CSV or Excel file."

    response = client.post(
        "/summary",
        files={
            "file": ("test.txt", txt_content, "text/plain")
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file type. Please upload a CSV or Excel file."
