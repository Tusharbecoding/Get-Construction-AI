from google import genai
from google.genai import types
from PIL import Image
import base64
from typing import List, Dict, Any
import os

class ChatService:
    def __init__(self, api_key: str):
        # Initialize client with API key
        self.client = genai.Client(api_key=api_key)
        
    def answer_question(self, question: str, relevant_pages: List[Dict]) -> Dict[str, Any]:
        """Answer question using both text and visual analysis"""
        
        if not relevant_pages:
            return {
                'response': "I couldn't find relevant pages in the document to answer your question.",
                'sources': [],
                'confidence': 0.0,
                'pages_analyzed': []
            }
        
        try:
            # Prepare content for vision model
            content_parts = []
            
            # Add system instruction and question
            system_prompt = self._create_system_prompt()
            content_parts.append(f"{system_prompt}\n\nUser Question: {question}\n")
            
            # Add page images and metadata
            pages_analyzed = []
            for page in relevant_pages:
                # Add page context
                page_context = self._build_page_context(page)
                content_parts.append(page_context)
                
                # Add image using PIL or bytes
                if os.path.exists(page['image_path']):
                    try:
                        # Method 1: PIL Image (preferred)
                        image = Image.open(page['image_path'])
                        content_parts.append(image)  # PIL images can be passed directly
                        pages_analyzed.append(page['page_number'])
                    except Exception as e:
                        # Method 2: Fallback to bytes with types.Part
                        try:
                            with open(page['image_path'], 'rb') as f:
                                image_bytes = f.read()
                            image_part = types.Part.from_bytes(
                                data=image_bytes, 
                                mime_type='image/png'
                            )
                            content_parts.append(image_part)
                            pages_analyzed.append(page['page_number'])
                        except Exception as e2:
                            print(f"Error loading image {page['image_path']}: PIL={e}, Bytes={e2}")
                            continue
            
            content_parts.append("\nPlease analyze the images and provide a detailed answer based on what you can see in the construction drawings:")
            
            # Generate response using correct API
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=content_parts
            )
            
            # Build sources
            sources = self._build_sources(relevant_pages)
            
            # Calculate confidence
            confidence = self._calculate_confidence(response.text, relevant_pages)
            
            return {
                'response': response.text,
                'sources': sources,
                'confidence': confidence,
                'pages_analyzed': pages_analyzed
            }
            
        except Exception as e:
            return {
                'response': f"Error analyzing the construction document: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'pages_analyzed': []
            }
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for construction document analysis"""
        return """You are a professional construction document assistant with expertise in reading architectural drawings, floor plans, elevations, and construction specifications.

CRITICAL INSTRUCTIONS:
1. Analyze both the text content AND the visual elements in the construction drawings
2. Look for measurements, dimensions, room labels, material callouts, and architectural symbols
3. Pay attention to floor plans, elevations, sections, and detail drawings
4. Only provide information that you can clearly see or read in the documents
5. When referencing information, specify which page and what type of drawing you're looking at
6. For measurements, read dimension lines, room sizes, and fixture dimensions from the drawings
7. For materials, look for material callouts, specifications, and notes on the drawings
8. If you cannot clearly see or read something in the drawings, say so explicitly
9. Provide specific page references for all information

CONSTRUCTION DRAWING TYPES YOU MAY SEE:
- Foundation Plans: Show footings, slabs, structural elements
- Floor Plans: Show room layouts, fixtures, dimensions
- Framing Plans: Show structural members, beams, joists
- Elevations: Show exterior views, materials, heights
- Sections: Show vertical cuts through the building
- Roof Plans: Show roof structure and materials
- Details: Show specific construction connections

Answer questions about sizes, materials, locations, specifications, and requirements based on what you can observe in the drawings."""
    
    def _build_page_context(self, page: Dict) -> str:
        """Build context text for a page"""
        context = f"\n--- PAGE {page['page_number']} ({page['page_type'].replace('_', ' ').title()}) ---\n"
        
        if page['text_content'].strip():
            context += f"Text Content: {page['text_content'][:500]}...\n"
        
        metadata = page.get('metadata', {})
        
        if metadata.get('rooms'):
            context += f"Rooms/Spaces: {', '.join(metadata['rooms'])}\n"
        
        if metadata.get('measurements'):
            context += f"Measurements Found: {', '.join(metadata['measurements'][:10])}\n"
        
        if metadata.get('materials'):
            context += f"Materials: {', '.join(metadata['materials'])}\n"
        
        if metadata.get('notes'):
            context += f"Notes: {'; '.join(metadata['notes'][:3])}\n"
        
        context += f"\n[IMAGE: {page['page_type'].replace('_', ' ').title()} drawing for Page {page['page_number']}]\n"
        
        return context
    
    def _build_sources(self, pages: List[Dict]) -> List[Dict[str, Any]]:
        """Build source references"""
        sources = []
        for page in pages:
            source = {
                'page': page['page_number'],
                'type': page['page_type'].replace('_', ' ').title(),
                'content_preview': page['text_content'][:200] + "..." if len(page['text_content']) > 200 else page['text_content'],
                'has_image': os.path.exists(page['image_path']),
                'rooms': page['metadata'].get('rooms', []),
                'measurements': page['metadata'].get('measurements', [])[:5]  # First 5 measurements
            }
            sources.append(source)
        
        return sources
    
    def _calculate_confidence(self, response: str, pages: List[Dict]) -> float:
        """Calculate response confidence based on various factors"""
        confidence = 0.5  # Base confidence
        
        # Boost if response references specific pages
        if any(f"page {page['page_number']}" in response.lower() for page in pages):
            confidence += 0.2
        
        # Boost if response includes specific measurements
        if any(measurement in response for page in pages for measurement in page['metadata'].get('measurements', [])):
            confidence += 0.15
        
        # Boost if response mentions seeing drawings/images
        vision_indicators = ['drawing', 'image', 'can see', 'visible', 'shown', 'depicted']
        if any(indicator in response.lower() for indicator in vision_indicators):
            confidence += 0.1
        
        # Reduce if response indicates uncertainty
        uncertainty_indicators = ['not clear', 'cannot see', 'not visible', 'unclear', 'not specified']
        if any(indicator in response.lower() for indicator in uncertainty_indicators):
            confidence -= 0.2
        
        return min(1.0, max(0.1, confidence))