import pymupdf  # PyMuPDF
from google import genai
from google.genai import types
from PIL import Image
import io
import base64
import os
from typing import List, Dict, Any
import uuid
import re
from datetime import datetime

class DocumentProcessor:
    def __init__(self):
        self.documents = {}  # In-memory storage
        self.image_storage_path = "temp_images"
        os.makedirs(self.image_storage_path, exist_ok=True)
        
    def process_pdf(self, file_content: bytes, filename: str) -> str:
        """Extract text and convert pages to images"""
        doc_id = str(uuid.uuid4())
        
        # Open PDF
        pdf_doc = pymupdf.open(stream=file_content, filetype="pdf")
        
        pages = []
        for page_num in range(len(pdf_doc)):
            page = pdf_doc.load_page(page_num)
            
            # Extract text
            text_content = page.get_text()
            
            # Convert page to image
            mat = pymupdf.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Save image
            image_filename = f"{doc_id}_page_{page_num + 1}.png"
            image_path = os.path.join(self.image_storage_path, image_filename)
            
            with open(image_path, "wb") as img_file:
                img_file.write(img_data)
            
            # Classify page type
            page_type = self._classify_page_type(text_content, page_num)
            
            # Extract metadata
            metadata = self._extract_page_metadata(text_content)
            
            page_data = {
                'page_number': page_num + 1,
                'text_content': text_content,
                'image_path': image_path,
                'page_type': page_type,
                'metadata': metadata
            }
            
            pages.append(page_data)
        
        pdf_doc.close()
        
        # Store document
        self.documents[doc_id] = {
            'filename': filename,
            'pages': pages,
            'processed_at': datetime.now()
        }
        
        return doc_id
    
    def _classify_page_type(self, text: str, page_num: int) -> str:
        """Classify what type of construction drawing this is"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['foundation plan', 'foundation', 'footing']):
            return 'foundation_plan'
        elif any(word in text_lower for word in ['floor plan', 'main floor', 'upper floor']):
            return 'floor_plan'
        elif any(word in text_lower for word in ['framing plan', 'framing', 'beam', 'joist']):
            return 'framing_plan'
        elif any(word in text_lower for word in ['elevation', 'front', 'rear', 'left', 'right']):
            return 'elevation'
        elif any(word in text_lower for word in ['section', 'building section']):
            return 'section'
        elif any(word in text_lower for word in ['roof plan', 'roof framing']):
            return 'roof_plan'
        elif any(word in text_lower for word in ['detail', 'wall detail', 'window detail']):
            return 'detail'
        else:
            return 'general'
    
    def _extract_page_metadata(self, text: str) -> Dict[str, Any]:
        """Extract structured metadata from page"""
        return {
            'measurements': self._extract_measurements(text),
            'rooms': self._extract_rooms(text),
            'materials': self._extract_materials(text),
            'symbols': self._extract_symbols(text),
            'notes': self._extract_notes(text)
        }
    
    def _extract_measurements(self, text: str) -> List[str]:
        """Extract measurements and dimensions"""
        patterns = [
            r"\d+'-\d+\"",  # 24'-6"
            r"\d+\"\s*x\s*\d+\"",  # 36" x 24"
            r"\d+'\s*x\s*\d+'",  # 12' x 8'
            r"\d+\.\d+\s*x\s*\d+\.\d+",  # 12.5 x 8.25
            r"\d+\s*sf",  # square feet
            r"\d+\s*sq\.?\s*ft",  # square feet
        ]
        
        measurements = []
        for pattern in patterns:
            measurements.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(measurements))  # Remove duplicates
    
    def _extract_rooms(self, text: str) -> List[str]:
        """Extract room names and spaces"""
        room_patterns = [
            r'kitchen', r'bathroom', r'bedroom', r'living room', r'dining room',
            r'garage', r'office', r'closet', r'pantry', r'laundry', r'foyer',
            r'great room', r'family room', r'master bedroom', r'guest bedroom',
            r'bonus room', r'media room', r'study', r'den', r'utility', r'mudroom',
            r'powder room', r'walk-in closet', r'entry', r'nook', r'loft'
        ]
        
        rooms = []
        text_lower = text.lower()
        for pattern in room_patterns:
            if re.search(pattern, text_lower):
                rooms.append(pattern.replace('r\'', '').replace('\'', ''))
        
        return list(set(rooms))
    
    def _extract_materials(self, text: str) -> List[str]:
        """Extract material specifications"""
        material_patterns = [
            r'concrete', r'steel', r'wood', r'lumber', r'drywall', r'gypsum',
            r'insulation', r'roofing', r'siding', r'flooring', r'tile', r'ceramic',
            r'carpet', r'hardwood', r'vinyl', r'granite', r'quartz', r'marble',
            r'stainless steel', r'aluminum', r'brick', r'stone', r'glass',
            r'laminate', r'engineered wood', r'composite'
        ]
        
        materials = []
        text_lower = text.lower()
        for pattern in material_patterns:
            if re.search(pattern, text_lower):
                materials.append(pattern)
        
        return list(set(materials))
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Extract architectural symbols and annotations"""
        symbols = []
        
        # Common architectural annotations
        symbol_patterns = [
            r'door', r'window', r'outlet', r'switch', r'light fixture',
            r'sink', r'toilet', r'bathtub', r'shower', r'stairs', r'fireplace',
            r'column', r'beam', r'wall', r'dimension'
        ]
        
        text_lower = text.lower()
        for pattern in symbol_patterns:
            if re.search(pattern, text_lower):
                symbols.append(pattern)
        
        return symbols
    
    def _extract_notes(self, text: str) -> List[str]:
        """Extract important notes and specifications"""
        notes = []
        
        # Look for note patterns
        note_patterns = [
            r'note:.*',
            r'see.*detail',
            r'typ\..*',
            r'typical.*',
            r'provide.*',
            r'install.*',
            r'verify.*'
        ]
        
        for pattern in note_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            notes.extend(matches)
        
        return notes[:10]  # Limit to first 10 notes
    
    def get_document_pages(self, doc_id: str) -> List[Dict]:
        """Get all pages for a document"""
        if doc_id in self.documents:
            return self.documents[doc_id]['pages']
        return []
    
    def get_relevant_pages(self, doc_id: str, query: str) -> List[Dict]:
        """Find pages most relevant to the query"""
        pages = self.get_document_pages(doc_id)
        if not pages:
            return []
        
        query_lower = query.lower()
        scored_pages = []
        
        for page in pages:
            score = 0
            
            # Score based on text content relevance
            text_lower = page['text_content'].lower()
            query_words = set(query_lower.split())
            text_words = set(text_lower.split())
            overlap = len(query_words.intersection(text_words))
            score += overlap
            
            # Boost score for page type relevance
            if any(word in query_lower for word in ['floor', 'room', 'layout', 'space']):
                if page['page_type'] in ['floor_plan']:
                    score += 5
            
            if any(word in query_lower for word in ['elevation', 'front', 'back', 'side']):
                if page['page_type'] == 'elevation':
                    score += 5
            
            if any(word in query_lower for word in ['foundation', 'basement']):
                if page['page_type'] == 'foundation_plan':
                    score += 5
            
            if any(word in query_lower for word in ['roof', 'attic']):
                if page['page_type'] == 'roof_plan':
                    score += 5
            
            # Boost for metadata matches
            for room in page['metadata'].get('rooms', []):
                if room in query_lower:
                    score += 3
            
            for material in page['metadata'].get('materials', []):
                if material in query_lower:
                    score += 2
            
            if score > 0:
                scored_pages.append((page, score))
        
        # Sort by relevance and return top 3 pages
        scored_pages.sort(key=lambda x: x[1], reverse=True)
        return [page for page, score in scored_pages[:3]]