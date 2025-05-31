import re
from typing import List

def normalize_unit_id(unit_text: str) -> str:
    """
    Normalize unit identifiers to a standard format.
    
    Args:
        unit_text: Raw unit text (e.g., "Unit I", "UNIT-1", "Unit-II")
    
    Returns:
        str: Normalized unit ID (e.g., "UNIT-I")
    """
    if not unit_text:
        return ""
    
    # Convert to uppercase and remove extra spaces
    unit_text = unit_text.upper().strip()
    
    # Extract unit number using regex
    match = re.search(r'UNIT[\s\-]*([IVX1-5]+)', unit_text)
    if match:
        unit_num = match.group(1)
        
        # Convert arabic numerals to roman numerals
        arabic_to_roman = {'1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V'}
        if unit_num in arabic_to_roman:
            unit_num = arabic_to_roman[unit_num]
        
        return f"UNIT-{unit_num}"
    
    return unit_text

def chunk_text_by_paragraphs(text: str, max_chunk_size: int = 1000) -> List[str]:
    """
    Chunk text by paragraphs with a maximum size limit.
    
    Args:
        text: Input text to chunk
        max_chunk_size: Maximum size of each chunk
    
    Returns:
        List[str]: List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Split by double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # If adding this paragraph would exceed max size, save current chunk
        if len(current_chunk) + len(paragraph) + 2 > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # If no paragraphs found, split by sentences
    if not chunks and text.strip():
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if not sentence.endswith('.'):
                sentence += '.'
            
            if len(current_chunk) + len(sentence) + 1 > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text.strip()]

def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text: Input text
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    
    return text.strip()

def extract_question_parts(question_text: str) -> dict:
    """
    Extract components from question text (e.g., "Unit I - 1a").
    
    Args:
        question_text: Question identifier text
    
    Returns:
        dict: Extracted components
    """
    result = {
        'unit': None,
        'question_number': None,
        'sub_part': None,
        'original': question_text
    }
    
    if not question_text:
        return result
    
    # Pattern to match "Unit I - 1a" or similar formats
    pattern = r'(?:Unit|UNIT)[\s\-]*([IVX1-5]+)[\s\-]*(\d+)([a-z]?)'
    match = re.search(pattern, question_text, re.IGNORECASE)
    
    if match:
        unit = match.group(1).upper()
        question_num = match.group(2)
        sub_part = match.group(3).lower() if match.group(3) else None
        
        # Normalize unit
        result['unit'] = normalize_unit_id(f"Unit {unit}")
        result['question_number'] = question_num
        result['sub_part'] = sub_part
    
    return result
