# Construction Document Chatter

A minimal prototype that allows users to upload construction documents (PDFs) and ask questions about them using AI vision analysis.

## Overview

This application enables users to:

- Upload construction documents (floor plans, elevations, specifications)
- Ask natural language questions about the documents
- Get AI-powered answers based on visual analysis of the drawings

**Example queries:**

- "What's the size of the bathtub on the second floor?"
- "What type of cooktop is specified in the kitchen?"
- "What are the dimensions of the master bedroom?"

## System Architecture & Reasoning

### High-Level Design Philosophy

**Goal**: Create the simplest possible working prototype that demonstrates AI-powered document Q&A.

**Architecture Decisions**:

1. **Monolithic Backend**: Single FastAPI service handling all operations

   - _Reasoning_: Eliminates service discovery, network complexity for prototype
   - _Trade-off_: Not microservice-ready, harder to scale individual components

2. **Vision-First Approach**: Convert all PDF pages to images, rely on vision model

   - _Reasoning_: Construction documents are primarily visual (plans, elevations)
   - _Trade-off_: Higher API costs, no text-based search optimization

3. **Stateless Frontend**: React with simple state management
   - _Reasoning_: Easy to understand, modify, and deploy
   - _Trade-off_: No offline capabilities, limited state persistence

### Data Flow

```
PDF Upload → PyMuPDF → Base64 Images → In-Memory Dict → Gemini Vision → Response
```

### Component Architecture

```
Frontend (Next.js)
├── UploadDocument.tsx    # File handling
├── Chat.tsx             # Conversation interface
└── page.tsx            # Main orchestration

Backend (FastAPI)
├── /api/upload         # PDF processing endpoint
├── /api/chat          # Q&A endpoint
└── In-memory storage  # Document persistence
```

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to use the application.

## Factual Grounding & Reliability

### Current Approach (Basic Implementation)

**What We Do**:

- Send all document pages to Gemini Vision model
- Instruct model to "only provide information you can clearly see"
- Include page references in responses

**What's Missing (Critical for Production)**:

- **No verification mechanism** - Can't validate if AI response matches document
- **No confidence scoring** - No way to assess answer reliability
- **No source highlighting** - Can't point to specific document sections
- **No fallback handling** - If model hallucinates, no detection system

### Production Factual Grounding Strategy

```python
# Multi-layer verification approach
1. OCR text extraction + vision analysis
2. Cross-reference text mentions with visual elements
3. Confidence scoring based on multiple evidence sources
4. Highlight specific document regions that support answer
5. Fallback to "information not clearly visible" for low confidence
```

## Key Trade-offs Made

### 1. **Simplicity vs. Accuracy**

- **Chose**: Minimal codebase, fast iteration
- **Sacrificed**: Rigorous answer verification, advanced document understanding
- **Impact**: Faster development but potential hallucinations

### 2. **Cost vs. Performance**

- **Chose**: Send all pages to vision model (simple)
- **Sacrificed**: Smart page selection, cost optimization
- **Impact**: Higher API costs but reliable coverage

### 3. **Storage vs. Persistence**

- **Chose**: In-memory storage (no setup complexity)
- **Sacrificed**: Document persistence, multi-user support
- **Impact**: Great for demo, unusable for production

### 4. **Flexibility vs. Optimization**

- **Chose**: Generic approach works for any construction document
- **Sacrificed**: Document-type-specific optimizations
- **Impact**: Broader applicability but suboptimal for specific use cases

## Current Implementation Details

### Simple & Minimal

- **95 lines of backend code** - No complex abstractions
- **In-memory storage** - Perfect for prototyping
- **Direct API calls** - No service layers or repositories
- **Base64 image encoding** - No file system dependencies

### Tech Stack

- **Backend**: FastAPI, PyMuPDF, google-genai, uvicorn
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **AI**: Google Gemini 1.5 Flash (Vision model)

## Production Enhancements

### Database & Storage

**Current**: In-memory dictionaries
**Production Options**:

- **PostgreSQL + S3**: Metadata in DB, images in cloud storage
- **MongoDB**: Document-oriented storage for flexible schemas
- **Redis**: Session caching and fast document retrieval

### Vector Databases & Search

**Current**: Send all pages to AI model
**Advanced Options**:

- **Pinecone/Weaviate**: Semantic search across document content
- **ChromaDB**: Open-source vector database for embeddings
- **Qdrant**: High-performance vector search with filtering

**Implementation Strategy**:

```python
# Generate embeddings for each page
embeddings = embed_model.encode(page_text)
vector_db.upsert(page_id, embeddings, metadata)

# Query-time: Find relevant pages first
similar_pages = vector_db.search(query_embedding, top_k=3)
# Then send only relevant pages to vision model
```

### Document Processing Pipeline

**Current**: Simple PDF → PNG conversion
**Production Enhancements**:

- **OCR Integration**: Tesseract for text extraction from scanned docs
- **Document Classification**: Auto-detect floor plans vs elevations vs specs
- **Multi-format Support**: CAD files, Word docs, images
- **Batch Processing**: Background job queues for large documents

### Scalability & Performance

**Current**: Single-threaded, synchronous processing
**Improvements**:

- **Async Processing**: Background tasks with Celery/RQ
- **Caching Layer**: Redis for frequently accessed documents
- **CDN Integration**: CloudFront for image delivery
- **Load Balancing**: Multiple backend instances

### Security & Authentication

**Current**: No authentication
**Production Requirements**:

- **User Authentication**: JWT tokens, OAuth integration
- **Document Privacy**: User-specific document access
- **API Rate Limiting**: Prevent abuse of AI endpoints
- **Input Validation**: Sanitize uploads and queries

### Monitoring & Analytics

**Production Additions**:

- **Logging**: Structured logging with correlation IDs
- **Metrics**: Document processing times, query accuracy
- **Error Tracking**: Sentry for production error monitoring
- **Usage Analytics**: Track popular query patterns

### AI Model Improvements

**Current**: Single Gemini model for all queries
**Advanced Options**:

- **Model Routing**: Different models for different query types
- **Fine-tuning**: Custom models trained on construction terminology
- **Multi-modal RAG**: Combine text embeddings with vision analysis
- **Confidence Scoring**: Better uncertainty quantification

### User Experience

**Enhancements**:

- **Progressive Web App**: Offline capability for cached documents
- **Real-time Collaboration**: Multiple users discussing same document
- **Annotation Tools**: Mark up documents with questions/answers
- **Export Features**: Save conversations as PDF reports
