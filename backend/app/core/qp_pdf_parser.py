import pdfplumber
import re
from typing import List, Dict
from app.core.llm_interface import call_gemini_llm

def parse_question_paper_pdf(pdf_filepath: str, course_name_from_subject: str) -> List[Dict]:
    """
    Parse question paper PDF into structured JSON format.
    
    Args:
        pdf_filepath: Path to the question paper PDF
        course_name_from_subject: Course name from subject context
    
    Returns:
        List[Dict]: Parsed questions in format [{'question': 'Unit I - 1a', 'text': '...'}]
    """
    try:
        # Extract text from PDF
        full_text = ""
        with pdfplumber.open(pdf_filepath) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
        
        if not full_text.strip():
            return []
        
        # Parse using Gemini LLM
        parsed_questions = parse_questions_with_gemini(full_text, course_name_from_subject)
        return parsed_questions
        
    except Exception as e:
        print(f"Error parsing question paper PDF {pdf_filepath}: {e}")
        return []

def parse_questions_with_gemini(text_content: str, course_name: str) -> List[Dict]:
    """
    Use Gemini LLM to parse question paper text into structured format.
    
    Args:
        text_content: Raw text from question paper
        course_name: Name of the course
    
    Returns:
        List[Dict]: Parsed questions
    """
    prompt = f"""
    You are an expert at parsing academic question papers. Parse the following question paper text into a structured JSON format.

    COURSE: {course_name}
    
    QUESTION PAPER TEXT:
    {text_content}
    
    Parse this into a flat list where each question/sub-question is a separate entry. 
    
    Rules:
    1. Identify questions by unit (Unit I, Unit II, etc.) and question numbers (1, 2, 3, etc.)
    2. Sub-parts should be separate entries (1a, 1b, 2a, 2b, etc.)
    3. Include the full question text for each entry
    4. Use format: "Unit X - Ya" where X is the unit (I, II, III, IV, V) and Ya is question number with sub-part
    
    Return ONLY a JSON array in this exact format:
    [
        {{"question": "Unit I - 1a", "text": "full question text here"}},
        {{"question": "Unit I - 1b", "text": "full question text here"}},
        {{"question": "Unit II - 2a", "text": "full question text here"}}
    ]
    
    Important: 
    - Return only the JSON array, no other text
    - Each question should be complete and standalone
    - Preserve all mathematical symbols and formatting as text
    """
    
    try:
        response = call_gemini_llm(prompt)
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            import json
            parsed_data = json.loads(json_match.group())
            
            # Validate the structure
            validated_questions = []
            for item in parsed_data:
                if isinstance(item, dict) and 'question' in item and 'text' in item:
                    validated_questions.append({
                        'question': str(item['question']).strip(),
                        'text': str(item['text']).strip()
                    })
            
            return validated_questions
        else:
            print("No valid JSON found in LLM response")
            return []
            
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return []
    except Exception as e:
        print(f"Error parsing questions with Gemini: {e}")
        return []

def extract_question_metadata(question_entry: Dict) -> Dict:
    """
    Extract metadata from a question entry.
    
    Args:
        question_entry: Question entry with 'question' and 'text' fields
    
    Returns:
        Dict: Extracted metadata
    """
    from app.utils.text_utils import extract_question_parts
    
    question_id = question_entry.get('question', '')
    question_text = question_entry.get('text', '')
    
    # Parse question components
    components = extract_question_parts(question_id)
    
    metadata = {
        'question_id': question_id,
        'unit': components.get('unit'),
        'question_number': components.get('question_number'),
        'sub_part': components.get('sub_part'),
        'text_length': len(question_text),
        'word_count': len(question_text.split()) if question_text else 0
    }
    
    return metadata

def validate_question_paper_structure(parsed_questions: List[Dict]) -> Dict:
    """
    Validate the structure of parsed question paper.
    
    Args:
        parsed_questions: List of parsed questions
    
    Returns:
        Dict: Validation result
    """
    validation_result = {
        'is_valid': True,
        'total_questions': len(parsed_questions),
        'units_found': set(),
        'warnings': [],
        'errors': []
    }
    
    if not parsed_questions:
        validation_result['is_valid'] = False
        validation_result['errors'].append("No questions found in the question paper")
        return validation_result
    
    # Check each question
    for i, question in enumerate(parsed_questions):
        if not isinstance(question, dict):
            validation_result['errors'].append(f"Question {i+1}: Invalid format")
            continue
        
        if 'question' not in question or 'text' not in question:
            validation_result['errors'].append(f"Question {i+1}: Missing required fields")
            continue
        
        # Extract unit information
        metadata = extract_question_metadata(question)
        unit = metadata.get('unit')
        if unit:
            validation_result['units_found'].add(unit)
        else:
            validation_result['warnings'].append(f"Question {i+1}: Could not identify unit")
    
    # Convert set to list for JSON serialization
    validation_result['units_found'] = list(validation_result['units_found'])
    
    # Check if we have reasonable number of questions
    if len(parsed_questions) < 5:
        validation_result['warnings'].append("Question paper seems to have very few questions")
    
    if validation_result['errors']:
        validation_result['is_valid'] = False
    
    return validation_result
