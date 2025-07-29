from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentUpload(BaseModel):
    filename: str
    content_type: str

class ChatMessage(BaseModel):
    message: str
    document_id: str

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    pages_analyzed: List[int]

class DocumentPage(BaseModel):
    page_number: int
    text_content: str
    image_path: str
    page_type: str  # 'floor_plan', 'elevation', 'section', 'detail', 'general'
    metadata: Dict[str, Any]

class DocumentChunk(BaseModel):
    id: str
    page_number: int
    text_content: str
    image_path: str
    content_type: str
    measurements: List[str]
    rooms: List[str]
    materials: List[str]