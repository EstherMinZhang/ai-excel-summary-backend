# AI Excel Summary Backend

This is a backend service that accepts CSV or Excel files and returns both a structured dataset summary and an AI-generated natural language summary.

## Project Structure

- `app/main.py`: FastAPI application entry point, exposing `/` and `/summary` endpoints.
- `app/excel_summary.py`: Reads CSV/Excel files and produces structured summary data.
- `app/ai_summary.py`: Calls Gemini AI (`google.genai`) to generate natural language summaries.
- `tests/test_main.py`: API endpoint tests.
- `requirements.txt`: Python dependency list.

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set the Gemini API key environment variable:

```powershell
setx GEMINI_API_KEY "your_gemini_api_key"
```

Or create a `.env` file in the project root with:

```env
GEMINI_API_KEY=your_gemini_api_key
```

## Running the Service

```powershell
uvicorn app.main:app --reload
```

The service will be available at `http://127.0.0.1:8000`.

## API Endpoints

### `GET /`

Returns a simple status message.

### `POST /summary`

Uploads a CSV or Excel file and returns a structured summary plus an AI-generated summary.

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/summary" -F "file=@data.xlsx"
```

## Notes

- This project does not include a custom frontend. The UI you see in the browser is FastAPI's built-in documentation interface.
- `app/excel_summary.py` extracts details such as sheet names, row counts, column counts, missing values, and data types.
- `app/ai_summary.py` sends the structured summary to Gemini and returns the AI model response.

## Testing

```powershell
pytest
```

## Additional Information

Make sure Python is installed and the virtual environment is activated before running the project.
