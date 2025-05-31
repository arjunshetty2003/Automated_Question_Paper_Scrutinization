import google.generativeai as genai
from flask import current_app
import time
import re
from typing import List, Dict, Optional

# Configure Gemini API
def configure_gemini():
    """Configure Gemini API with the API key."""
    api_key = current_app.config.get('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
    else:
        raise ValueError("GEMINI_API_KEY not found in configuration")

def get_generative_model():
    """Get configured Gemini generative model."""
    configure_gemini()
    model_name = current_app.config.get('GENERATIVE_MODEL_NAME', 'gemini-1.5-flash')
    return genai.GenerativeModel(model_name)

def call_gemini_llm(prompt_text: str, max_retries: int = 3) -> str:
    """
    Call Gemini LLM with retry logic.
    
    Args:
        prompt_text: The prompt to send to the model
        max_retries: Maximum number of retry attempts
    
    Returns:
        str: Generated response text
    """
    model = get_generative_model()
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt_text)
            if response.text:
                return response.text.strip()
            else:
                print(f"Empty response from Gemini on attempt {attempt + 1}")
        except Exception as e:
            print(f"Error calling Gemini LLM (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise e
    
    return ""

def check_syllabus_coverage_with_gemini(question_text: str, syllabus_context: str, unit_info: str) -> Dict:
    """
    Check if a question is covered by the syllabus using Gemini.
    
    Args:
        question_text: The question to validate
        syllabus_context: Relevant syllabus content
        unit_info: Unit information
    
    Returns:
        dict: Validation result with coverage status and reasoning
    """
    prompt = f"""
    You are an expert academic evaluator. Analyze whether the following question is covered by the provided syllabus content.

    UNIT INFORMATION: {unit_info}
    
    QUESTION TO VALIDATE:
    {question_text}
    
    RELEVANT SYLLABUS CONTENT:
    {syllabus_context}
    
    Evaluate if this question is covered by the syllabus content. Consider:
    1. Direct topic coverage
    2. Conceptual alignment
    3. Learning objectives
    4. Depth and scope
    
    Respond in the following JSON format only:
    {{
        "is_covered": true/false,
        "coverage_percentage": 0-100,
        "reasoning": "detailed explanation of why the question is/isn't covered",
        "relevant_topics": ["list", "of", "relevant", "syllabus", "topics"],
        "recommendations": "suggestions if not covered or partially covered"
    }}
    """
    
    try:
        response = call_gemini_llm(prompt)
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            import json
            return json.loads(json_match.group())
        else:
            return {
                "is_covered": False,
                "coverage_percentage": 0,
                "reasoning": "Unable to parse LLM response",
                "relevant_topics": [],
                "recommendations": "Manual review required"
            }
    except Exception as e:
        print(f"Error in syllabus coverage check: {e}")
        return {
            "is_covered": False,
            "coverage_percentage": 0,
            "reasoning": f"Error during validation: {str(e)}",
            "relevant_topics": [],
            "recommendations": "Manual review required due to technical error"
        }

def check_textbook_coverage_with_gemini(question_text: str, textbook_context: str, unit_info: str) -> Dict:
    """
    Check if a question is supported by textbook content using Gemini.
    
    Args:
        question_text: The question to validate
        textbook_context: Relevant textbook content
        unit_info: Unit information
    
    Returns:
        dict: Validation result with support status and details
    """
    prompt = f"""
    You are an expert academic evaluator. Analyze whether the following question can be answered using the provided textbook content.

    UNIT INFORMATION: {unit_info}
    
    QUESTION TO VALIDATE:
    {question_text}
    
    RELEVANT TEXTBOOK CONTENT:
    {textbook_context}
    
    Evaluate if this question can be adequately answered using the textbook content. Consider:
    1. Information availability
    2. Content depth and detail
    3. Examples and explanations
    4. Conceptual coverage
    
    Respond in the following JSON format only:
    {{
        "is_supported": true/false,
        "support_percentage": 0-100,
        "reasoning": "detailed explanation of textbook support",
        "content_gaps": ["list", "of", "missing", "information"],
        "available_content": ["list", "of", "relevant", "textbook", "sections"],
        "recommendations": "suggestions for improvement"
    }}
    """
    
    try:
        response = call_gemini_llm(prompt)
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            import json
            return json.loads(json_match.group())
        else:
            return {
                "is_supported": False,
                "support_percentage": 0,
                "reasoning": "Unable to parse LLM response",
                "content_gaps": ["Response parsing error"],
                "available_content": [],
                "recommendations": "Manual review required"
            }
    except Exception as e:
        print(f"Error in textbook coverage check: {e}")
        return {
            "is_supported": False,
            "support_percentage": 0,
            "reasoning": f"Error during validation: {str(e)}",
            "content_gaps": [f"Technical error: {str(e)}"],
            "available_content": [],
            "recommendations": "Manual review required due to technical error"
        }
