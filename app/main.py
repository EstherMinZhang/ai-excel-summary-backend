from fastapi import FastAPI, UploadFile, File, HTTPException
from app.excel_summary import summarize_excel_file
from app.ai_summary import generate_ai_summary

app = FastAPI(title="AI Excel Summary Backend")


@app.get("/")
def root():
    return {
        "message": "AI Excel Summary Backend is running."
    }


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
