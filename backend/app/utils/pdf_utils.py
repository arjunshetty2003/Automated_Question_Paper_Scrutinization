import os
import re
import json
import pdfplumber

class SimpleDocument:
    """Helper class for Documents"""
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}
    
    def __repr__(self):
        return f"SimpleDocument(page_content='{self.page_content[:50].replace(chr(10), ' ')}...', metadata={self.metadata})"

def extract_text_from_pdf_paged(pdf_path):
    """Extract text from PDF file, returning a list of dictionaries with page numbers and text"""
    pages_text_content = []
    if not pdf_path or not os.path.exists(pdf_path):
        return pages_text_content
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text(x_tolerance=2, y_tolerance=2, layout=False)
                if text and text.strip():
                    cleaned_text = re.sub(r'\n\s*\n+', '\n\n', text.strip())
                    pages_text_content.append({"page_number": i + 1, "text": cleaned_text})
    except Exception as e:
        print(f"Error reading or processing PDF '{pdf_path}': {e}")
    
    return pages_text_content

def chunk_text_by_paragraphs(text, min_chunk_len=50, max_chunk_len=700):
    """Chunk text into paragraphs of reasonable size for embedding"""
    if not text:
        return []
    
    paragraphs = re.split(r'\n\s*\n+', text.strip())
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        if not current_chunk:
            current_chunk = para
        elif len(current_chunk) + len(para) + 1 <= max_chunk_len:  # +1 for newline
            current_chunk += "\n\n" + para
        else:
            if len(current_chunk) >= min_chunk_len:
                chunks.append(current_chunk)
            current_chunk = para
    
    if current_chunk and len(current_chunk) >= min_chunk_len:
        chunks.append(current_chunk)

    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_len:  # Further split if a single paragraph was too long
            for i in range(0, len(chunk), max_chunk_len):
                final_chunks.append(chunk[i:i+max_chunk_len])
        elif len(chunk) >= min_chunk_len:  # Ensure chunk is not too small
            final_chunks.append(chunk)
    
    return final_chunks

def normalize_unit_id(unit_id_str):
    """Normalize unit ID for consistent comparison"""
    if not unit_id_str:
        return "UNIT-UNKNOWN"
    
    normalized = unit_id_str.upper().replace(" ", "").replace("_", "")
    match = re.match(r"(UNIT)([IVXLCDM\d]+)", normalized)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    
    return normalized

def load_syllabus_from_json(file_path):
    """Load syllabus from JSON file and convert to document format"""
    documents = []
    if not file_path or not os.path.exists(file_path):
        return documents, None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        course_name = data.get("course_name", "Unknown Course")
        units_data = []
        
        for unit_data in data.get("units", []):
            unit_id_val = normalize_unit_id(unit_data.get("unit", "Unknown Unit"))
            unit_title_val = unit_data.get("title", "Untitled")
            syllabus_content = unit_data.get("syllabus_content", "").strip()
            
            # Store unit data for later reference
            units_data.append({
                "unit_id": unit_id_val,
                "title": unit_title_val,
                "content": syllabus_content
            })
            
            if syllabus_content:
                content_chunks = chunk_text_by_paragraphs(syllabus_content, min_chunk_len=50, max_chunk_len=400)
                if not content_chunks and syllabus_content:
                    content_chunks = [syllabus_content]
                
                for i, chunk_cont in enumerate(content_chunks):
                    documents.append(SimpleDocument(
                        chunk_cont,
                        {
                            "source_type": "syllabus",
                            "course_name": course_name,
                            "unit_id": unit_id_val,
                            "unit_title": unit_title_val,
                            "chunk_id": f"syl_chunk_{unit_id_val.replace('-', '')}_{i}"
                        }
                    ))
    except Exception as e:
        print(f"Error loading or processing syllabus JSON from '{file_path}': {e}")
        return documents, None
    
    return documents, {"course_name": course_name, "units": units_data}

def prepare_textbook_documents(pdf_path):
    """Process a textbook PDF and return document chunks"""
    documents = []
    if not pdf_path or not os.path.exists(pdf_path):
        return documents
    
    # Extract text from PDF
    pages_data = extract_text_from_pdf_paged(pdf_path)
    if not pages_data:
        return documents
    
    doc_name = os.path.basename(pdf_path)
    safe_doc_name_part = re.sub(r'[^a-zA-Z0-9_-]', '_', doc_name.replace('.pdf', ''))
    
    # Combine all pages into a single text
    full_textbook_text = "\n\n".join([page_info["text"] for page_info in pages_data])
    
    # Chunk the text
    textbook_chunks = chunk_text_by_paragraphs(full_textbook_text, min_chunk_len=200, max_chunk_len=800)
    
    # Create document objects
    for i, chunk_content in enumerate(textbook_chunks):
        documents.append(SimpleDocument(
            chunk_content,
            {
                "source_type": "textbook",
                "document_name": doc_name,
                "chunk_id": f"tb_chunk_{safe_doc_name_part}_{i}"
            }
        ))
    
    return documents

def load_question_paper_from_json(file_path):
    """Load question paper from JSON file"""
    questions = []
    if not file_path or not os.path.exists(file_path):
        return questions
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            questions = data
        else:
            # Handle other formats
            questions = data.get("questions", [])
    except Exception as e:
        print(f"Error loading or processing question paper JSON from '{file_path}': {e}")
    
    return questions 