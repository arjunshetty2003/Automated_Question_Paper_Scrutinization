from typing import Dict, List
from app.utils.text_utils import normalize_unit_id, chunk_text_by_paragraphs
from app.core.embedding_manager import SimpleDocument

def parse_admin_syllabus_form(form_data: Dict) -> Dict:
    """
    Parse admin syllabus form data into standard JSON structure.
    
    Args:
        form_data: Form data with course_name and unit information
    
    Returns:
        dict: Structured syllabus JSON
    """
    syllabus_json = {
        'course_name': form_data.get('course_name', ''),
        'units': []
    }
    
    # Process units I through V
    for i in range(1, 6):
        unit_key = f'unit_{i}'
        title_key = f'unit_{i}_title'
        content_key = f'unit_{i}_content'
        
        if title_key in form_data and content_key in form_data:
            unit_data = {
                'unit': f'UNIT-{["", "I", "II", "III", "IV", "V"][i]}',
                'title': form_data[title_key].strip(),
                'syllabus_content': form_data[content_key].strip()
            }
            
            # Only add units with content
            if unit_data['title'] or unit_data['syllabus_content']:
                syllabus_json['units'].append(unit_data)
    
    return syllabus_json

def process_syllabus_for_embedding(syllabus_json: Dict) -> List[SimpleDocument]:
    """
    Process syllabus JSON into SimpleDocument objects for embedding.
    
    Args:
        syllabus_json: Structured syllabus data
    
    Returns:
        List[SimpleDocument]: Documents ready for embedding
    """
    documents = []
    course_name = syllabus_json.get('course_name', '')
    
    for unit in syllabus_json.get('units', []):
        unit_id = normalize_unit_id(unit.get('unit', ''))
        unit_title = unit.get('title', '')
        unit_content = unit.get('syllabus_content', '')
        
        # Combine title and content for chunking
        full_content = f"{unit_title}\n\n{unit_content}".strip()
        
        if full_content:
            # Chunk the content
            chunks = chunk_text_by_paragraphs(full_content, max_chunk_size=800)
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    'source_type': 'syllabus',
                    'course_name': course_name,
                    'unit_id': unit_id,
                    'unit_title': unit_title,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                
                doc = SimpleDocument(content=chunk, metadata=metadata)
                documents.append(doc)
    
    return documents

def validate_syllabus_data(syllabus_json: Dict) -> List[str]:
    """
    Validate syllabus data structure.
    
    Args:
        syllabus_json: Syllabus data to validate
    
    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []
    
    if not syllabus_json.get('course_name'):
        errors.append("Course name is required")
    
    units = syllabus_json.get('units', [])
    if not units:
        errors.append("At least one unit is required")
    
    for i, unit in enumerate(units):
        unit_num = i + 1
        
        if not unit.get('unit'):
            errors.append(f"Unit {unit_num}: Unit identifier is required")
        
        if not unit.get('title'):
            errors.append(f"Unit {unit_num}: Unit title is required")
        
        if not unit.get('syllabus_content'):
            errors.append(f"Unit {unit_num}: Unit content is required")
    
    return errors
