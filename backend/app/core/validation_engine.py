from typing import Dict, List, Optional, Tuple
from app.core.embedding_manager import get_gemini_embeddings, load_vector_store_for_subject
from app.core.llm_interface import check_syllabus_coverage_with_gemini, check_textbook_coverage_with_gemini
from app.utils.text_utils import extract_question_parts
from app.db.mongo_db import MongoDBManager

def process_single_question_entry(
    question_entry: Dict,
    syllabus_vector_store,
    textbook_vector_store,
    subject_info: Dict
) -> Dict:
    """
    Process a single question entry for validation.
    
    Args:
        question_entry: Question with 'question' and 'text' fields
        syllabus_vector_store: FAISS vector store for syllabus
        textbook_vector_store: FAISS vector store for textbook
        subject_info: Subject information
    
    Returns:
        Dict: Validation result for the question
    """
    question_id = question_entry.get('question', '')
    question_text = question_entry.get('text', '')
    
    # Extract question components
    question_parts = extract_question_parts(question_id)
    
    result = {
        'question_id': question_id,
        'question_text': question_text,
        'unit': question_parts.get('unit'),
        'question_number': question_parts.get('question_number'),
        'sub_part': question_parts.get('sub_part'),
        'syllabus_validation': None,
        'textbook_validation': None,
        'overall_score': 0,
        'recommendations': []
    }
    
    try:
        # Search syllabus for relevant content
        syllabus_context = ""
        if syllabus_vector_store:
            syllabus_results = syllabus_vector_store.search(question_text, k=3)
            syllabus_context = "\n\n".join([doc.content for doc, score in syllabus_results])
        
        # Search textbook for relevant content
        textbook_context = ""
        if textbook_vector_store:
            textbook_results = textbook_vector_store.search(question_text, k=3)
            textbook_context = "\n\n".join([doc.content for doc, score in textbook_results])
        
        # Validate against syllabus
        if syllabus_context:
            unit_info = f"Unit: {question_parts.get('unit', 'Unknown')}, Question: {question_parts.get('question_number', 'Unknown')}"
            result['syllabus_validation'] = check_syllabus_coverage_with_gemini(
                question_text, syllabus_context, unit_info
            )
        else:
            result['syllabus_validation'] = {
                'is_covered': False,
                'coverage_percentage': 0,
                'reasoning': 'No relevant syllabus content found',
                'relevant_topics': [],
                'recommendations': 'Add syllabus content for this topic'
            }
        
        # Validate against textbook
        if textbook_context:
            unit_info = f"Unit: {question_parts.get('unit', 'Unknown')}, Question: {question_parts.get('question_number', 'Unknown')}"
            result['textbook_validation'] = check_textbook_coverage_with_gemini(
                question_text, textbook_context, unit_info
            )
        else:
            result['textbook_validation'] = {
                'is_supported': False,
                'support_percentage': 0,
                'reasoning': 'No relevant textbook content found',
                'content_gaps': ['No textbook content available'],
                'available_content': [],
                'recommendations': 'Add textbook content for this topic'
            }
        
        # Calculate overall score
        syllabus_score = result['syllabus_validation'].get('coverage_percentage', 0)
        textbook_score = result['textbook_validation'].get('support_percentage', 0)
        result['overall_score'] = (syllabus_score + textbook_score) / 2
        
        # Generate recommendations
        recommendations = []
        if syllabus_score < 70:
            recommendations.append("Review syllabus alignment for this question")
        if textbook_score < 70:
            recommendations.append("Ensure adequate textbook coverage for this topic")
        if result['overall_score'] < 60:
            recommendations.append("Consider revising this question or improving course materials")
        
        result['recommendations'] = recommendations
        
    except Exception as e:
        print(f"Error processing question {question_id}: {e}")
        result['syllabus_validation'] = {
            'is_covered': False,
            'coverage_percentage': 0,
            'reasoning': f'Error during validation: {str(e)}',
            'relevant_topics': [],
            'recommendations': 'Manual review required'
        }
        result['textbook_validation'] = {
            'is_supported': False,
            'support_percentage': 0,
            'reasoning': f'Error during validation: {str(e)}',
            'content_gaps': ['Technical error'],
            'available_content': [],
            'recommendations': 'Manual review required'
        }
    
    return result

def validate_question_paper(parsed_qp_json_list: List[Dict], subject_id: str) -> Dict:
    """
    Validate an entire question paper against subject materials.
    
    Args:
        parsed_qp_json_list: List of parsed questions
        subject_id: Subject ID
    
    Returns:
        Dict: Complete validation results
    """
    # Get subject information
    subject_info = MongoDBManager.get_subject_by_id(subject_id)
    if not subject_info:
        return {
            'success': False,
            'error': 'Subject not found',
            'results': []
        }
    
    # Load vector stores
    syllabus_vector_store = load_vector_store_for_subject(subject_id, 'syllabus')
    textbook_vector_store = load_vector_store_for_subject(subject_id, 'textbook')
    
    if not syllabus_vector_store and not textbook_vector_store:
        return {
            'success': False,
            'error': 'No syllabus or textbook content available for validation',
            'results': []
        }
    
    # Process each question
    validation_results = []
    for question_entry in parsed_qp_json_list:
        question_result = process_single_question_entry(
            question_entry,
            syllabus_vector_store,
            textbook_vector_store,
            subject_info
        )
        validation_results.append(question_result)
    
    # Calculate summary statistics
    summary = calculate_validation_summary(validation_results)
    
    return {
        'success': True,
        'subject_name': subject_info.get('name', ''),
        'total_questions': len(validation_results),
        'summary': summary,
        'results': validation_results
    }

def calculate_validation_summary(validation_results: List[Dict]) -> Dict:
    """
    Calculate summary statistics for validation results.
    
    Args:
        validation_results: List of validation results
    
    Returns:
        Dict: Summary statistics
    """
    if not validation_results:
        return {}
    
    # Calculate averages
    total_questions = len(validation_results)
    syllabus_scores = []
    textbook_scores = []
    overall_scores = []
    
    syllabus_covered = 0
    textbook_supported = 0
    
    units_coverage = {}
    
    for result in validation_results:
        # Syllabus scores
        if result.get('syllabus_validation'):
            syllabus_score = result['syllabus_validation'].get('coverage_percentage', 0)
            syllabus_scores.append(syllabus_score)
            if result['syllabus_validation'].get('is_covered', False):
                syllabus_covered += 1
        
        # Textbook scores
        if result.get('textbook_validation'):
            textbook_score = result['textbook_validation'].get('support_percentage', 0)
            textbook_scores.append(textbook_score)
            if result['textbook_validation'].get('is_supported', False):
                textbook_supported += 1
        
        # Overall scores
        overall_scores.append(result.get('overall_score', 0))
        
        # Unit coverage
        unit = result.get('unit')
        if unit:
            if unit not in units_coverage:
                units_coverage[unit] = {'total': 0, 'covered': 0, 'supported': 0}
            units_coverage[unit]['total'] += 1
            if result.get('syllabus_validation', {}).get('is_covered', False):
                units_coverage[unit]['covered'] += 1
            if result.get('textbook_validation', {}).get('is_supported', False):
                units_coverage[unit]['supported'] += 1
    
    summary = {
        'average_syllabus_score': sum(syllabus_scores) / len(syllabus_scores) if syllabus_scores else 0,
        'average_textbook_score': sum(textbook_scores) / len(textbook_scores) if textbook_scores else 0,
        'average_overall_score': sum(overall_scores) / len(overall_scores) if overall_scores else 0,
        'syllabus_coverage_percentage': (syllabus_covered / total_questions) * 100,
        'textbook_support_percentage': (textbook_supported / total_questions) * 100,
        'units_coverage': units_coverage,
        'grade': get_overall_grade(sum(overall_scores) / len(overall_scores) if overall_scores else 0)
    }
    
    return summary

def get_overall_grade(score: float) -> str:
    """Get letter grade based on overall score."""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'
