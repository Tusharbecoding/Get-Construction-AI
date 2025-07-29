from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import pymupdf
import uuid
import base64
import os
import uvicorn
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

client = genai.Client(api_key=GOOGLE_API_KEY)

documents = {}

class ChatMessage(BaseModel):
    message: str
    document_id: str

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Only PDF files supported")
    
    doc_id = str(uuid.uuid4())
    content = await file.read()
    
    pdf = pymupdf.open(stream=content, filetype="pdf")
    images = []
    
    for page_num in range(len(pdf)):
        page = pdf.load_page(page_num)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        img_b64 = base64.b64encode(img_bytes).decode()
        images.append(img_b64)
    
    pdf.close()
    
    documents[doc_id] = {
        'filename': file.filename,
        'images': images
    }
    
    return {
        "document_id": doc_id,
        "filename": file.filename,
        "status": "processed"
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    if message.document_id not in documents:
        raise HTTPException(404, "Document not found")
    
    doc = documents[message.document_id]
    
    system_prompt = """You are a construction document expert. Answer questions about this construction document based on what you can see in the images. Be specific about measurements, materials, and locations."""

    content_parts = [
        system_prompt,
        f"Question: {message.message}"
    ]
    
    for img_b64 in doc['images']:
        img_bytes = base64.b64decode(img_b64)
        image_part = types.Part.from_bytes(data=img_bytes, mime_type='image/png')
        content_parts.append(image_part)
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=content_parts,
            config=types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.8
            )
        )
        
        return {
            "response": response.text,
            "sources": [{"page": i+1, "content_preview": "Construction drawing"} for i in range(len(doc['images']))]
        }
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)