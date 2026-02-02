from fastapi import FastAPI, UploadFile, File, HTTPException
import pytesseract
from pdf2image import convert_from_bytes
import io

app = FastAPI()
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
# Remove 'async' so FastAPI handles this in a thread pool
@app.post("/extract-text")
def extract_text(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        pdf_content = file.file.read()
        
        # Convert PDF to list of images
        pages = convert_from_bytes(pdf_content, dpi=300)
        
        full_text = []
        for i, page in enumerate(pages):
            # Process OCR
            text = pytesseract.image_to_string(page)
            full_text.append(f"--- Page {i+1} ---\n{text}")
            
            # Optional: Clear image from memory immediately after processing
            page.close() 
            
        return {
            "filename": file.filename, 
            "page_count": len(pages),
            "text": "\n".join(full_text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "OCR API is running!"}