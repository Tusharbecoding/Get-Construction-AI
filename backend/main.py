from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from document_processor import DocumentProcessor
from chat_service import ChatService
from models import ChatMessage, ChatResponse
import logging


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Construction Document Chat API - Vision Enhanced")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
chat_service = ChatService(api_key="")

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a construction document with vision analysis"""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Process document (extract text + convert to images)
        doc_id = document_processor.process_pdf(content, file.filename)
        
        # Get processing summary
        pages = document_processor.get_document_pages(doc_id)
        page_types = list(set([page['page_type'] for page in pages]))
        
        logger.info(f"Successfully processed document: {file.filename} with ID: {doc_id}")
        logger.info(f"Pages: {len(pages)}, Types: {page_types}")
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "status": "processed",
            "pages_count": len(pages),
            "page_types": page_types
        }
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Answer questions using vision analysis of construction drawings"""
    try:
        # Get relevant pages for the query
        relevant_pages = document_processor.get_relevant_pages(message.document_id, message.message)
        
        if not relevant_pages:
            raise HTTPException(status_code=404, detail="No relevant pages found for this question")
        
        # Generate response using vision model
        result = chat_service.answer_question(message.message, relevant_pages)
        
        logger.info(f"Generated vision-based response for: {message.message[:50]}...")
        logger.info(f"Analyzed pages: {result['pages_analyzed']}")
        
        return ChatResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/api/document/{doc_id}/pages")
async def get_document_pages(doc_id: str):
    """Get summary of document pages"""
    try:
        pages = document_processor.get_document_pages(doc_id)
        
        if not pages:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Return summary without full content
        summary = []
        for page in pages:
            summary.append({
                'page_number': page['page_number'],
                'page_type': page['page_type'],
                'rooms': page['metadata'].get('rooms', []),
                'measurements_count': len(page['metadata'].get('measurements', [])),
                'materials': page['metadata'].get('materials', [])
            })
        
        return {'pages': summary}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document pages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "vision_enabled": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)