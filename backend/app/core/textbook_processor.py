import pdfplumber
from typing import List, Dict
from app.utils.text_utils import chunk_text_by_paragraphs
from app.core.embedding_manager import SimpleDocument

def process_textbook_pdf(pdf_filepath: str) -> List[SimpleDocument]:
    """
    Process a textbook PDF into SimpleDocument objects for embedding.
    
    Args:
        pdf_filepath: Path to the PDF file
    
    Returns:
        List[SimpleDocument]: Documents ready for embedding
    """
    documents = []
    
    try:
        with pdfplumber.open(pdf_filepath) as pdf:
            full_text = ""
            
            # Extract text from all pages
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
            
            if full_text.strip():
                # Get filename for metadata
                import os
                filename = os.path.basename(pdf_filepath)
                
                # Chunk the entire text
                chunks = chunk_text_by_paragraphs(full_text, max_chunk_size=1000)
                
                for i, chunk in enumerate(chunks):
                    metadata = {
                        'source_type': 'textbook',
                        'document_name': filename,
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                    
                    doc = SimpleDocument(content=chunk, metadata=metadata)
                    documents.append(doc)
    
    except Exception as e:
        print(f"Error processing textbook PDF {pdf_filepath}: {e}")
    
    return documents

def extract_text_from_pdf(pdf_filepath: str) -> str:
    """
    Extract raw text from PDF file.
    
    Args:
        pdf_filepath: Path to the PDF file
    
    Returns:
        str: Extracted text
    """
    try:
        with pdfplumber.open(pdf_filepath) as pdf:
            text_content = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n\n"
            return text_content.strip()
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_filepath}: {e}")
        return ""

def validate_pdf_file(pdf_filepath: str) -> Dict[str, any]:
    """
    Validate PDF file and extract basic information.
    
    Args:
        pdf_filepath: Path to the PDF file
    
    Returns:
        dict: Validation result with file info
    """
    result = {
        'is_valid': False,
        'page_count': 0,
        'has_text': False,
        'file_size_mb': 0,
        'error': None
    }
    
    try:
        import os
        if not os.path.exists(pdf_filepath):
            result['error'] = "File does not exist"
            return result
        
        # Get file size
        result['file_size_mb'] = os.path.getsize(pdf_filepath) / (1024 * 1024)
        
        with pdfplumber.open(pdf_filepath) as pdf:
            result['page_count'] = len(pdf.pages)
            
            # Check if PDF has extractable text
            for page in pdf.pages[:3]:  # Check first 3 pages
                if page.extract_text():
                    result['has_text'] = True
                    break
            
            result['is_valid'] = True
            
    except Exception as e:
        result['error'] = str(e)
    
    return result
