from fastapi import FastAPI, UploadFile
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from pypdf import PdfReader
import io

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database_connected": True, "result": result.scalar()}

@app.post("/upload")
async def upload_document(file: UploadFile):
    contents = await file.read()
    reader = PdfReader(io.BytesIO(contents))
    
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    return {
        "filename": file.filename,
        "page_count": len(reader.pages),
        "extracted_text_preview": text[:200]
    }