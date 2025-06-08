import os
import re
import json
import time
from flask import current_app
from ..utils.embedding_utils import GeminiEmbeddingProvider
from ..utils.simple_vector_store import SimpleVectorStoreFAISS

def format_retrieved_context_for_llm(retrieved_items, source_type_name):
    """Format retrieved documents into a prompt-friendly format"""
    if not retrieved_items:
        return f"No relevant {source_type_name} sections found during retrieval."
    
    context_str = f"--- Relevant {source_type_name} Sections (top {len(retrieved_items)}) ---\n"
    valid_contexts_found = 0
    
    for i, item in enumerate(retrieved_items):
        if "document" not in item or not hasattr(item["document"], "page_content") or not hasattr(item["document"], "metadata"):
            continue
            
        doc = item["document"]
        page_content_clean = str(doc.page_content).strip()
        
        if not page_content_clean:
            continue
            
        valid_contexts_found += 1
        metadata_str_parts = []
        
        if doc.metadata.get("unit_id"):
            metadata_str_parts.append(f"Unit: {doc.metadata['unit_id']}")
            
        if doc.metadata.get("unit_title"):
            metadata_str_parts.append(f"Title: {doc.metadata['unit_title']}")
            
        if doc.metadata.get("document_name"):
            metadata_str_parts.append(f"Doc: {doc.metadata['document_name']}")
            
        if doc.metadata.get("chunk_id"):
            metadata_str_parts.append(f"ChunkID: {doc.metadata['chunk_id']}")
            
        metadata_display = ", ".join(metadata_str_parts) if metadata_str_parts else "N/A"
        context_str += f"Context {valid_contexts_found}: (Metadata: {metadata_display}; Distance: {item.get('distance', -1):.4f})\nContent: {page_content_clean[:700]}...\n\n"
    
    if valid_contexts_found == 0:
        return f"No relevant (non-empty) {source_type_name} sections found after filtering."
    
    return context_str.strip()

def check_syllabus_coverage(question_details, retrieved_syllabus_items, gemini_provider):
    """Check if a question is covered in the syllabus using Gemini"""
    q_unit = question_details["q_paper_unit"]
    q_num = question_details["q_paper_num"]
    q_sub = question_details["q_paper_subpart"]
    q_text = question_details["question_text"]
    
    syllabus_context_str = format_retrieved_context_for_llm(retrieved_syllabus_items, "Syllabus")
    
    prompt = f"""You are an expert academic assistant evaluating if an exam question is covered by a given syllabus.
Question Details from Exam Paper:
Unit (from QP ID): {q_unit}
Question Number (from QP ID): {q_num}{q_sub}
Question Text: "{q_text}"

{syllabus_context_str}

Based *solely* on the "Relevant Syllabus Sections" provided above (if any):
1. Is the question IN SYLLABUS or OUT OF SYLLABUS?
2. If IN SYLLABUS, briefly state which syllabus unit and title appear to cover it from the provided context, and quote the most relevant part of the syllabus text that supports this.
3. If OUT OF SYLLABUS, briefly explain why it is not covered by the provided syllabus sections (e.g., topic not mentioned, depth beyond scope, or no relevant syllabus context found).

Your response MUST start with "SYLLABUS_VERDICT: IN_SYLLABUS" or "SYLLABUS_VERDICT: OUT_OF_SYLLABUS".
Immediately after the verdict, on a new line, provide your reasoning starting with "REASONING: ".
Example IN SYLLABUS response:
SYLLABUS_VERDICT: IN_SYLLABUS
REASONING: The question is covered under syllabus unit 'UNIT-I: Introduction to Operating Systems' as it directly asks about 'System Calls', which is listed in the syllabus content: "System Structures- Operating System Services, System calls...".

Example OUT OF SYLLABUS response:
SYLLABUS_VERDICT: OUT_OF_SYLLABUS
REASONING: The topic of 'Advanced Quantum Entanglement in OS Design' is not mentioned in any of the provided syllabus sections, which focus on classical operating system concepts.
"""
    
    raw_text_response = gemini_provider.get_completion(prompt)
    verdict, reasoning = "ERROR_PARSING_LLM_RESPONSE", "Could not parse LLM response for syllabus."
    
    if raw_text_response.startswith("ERROR_LLM_"):
        verdict, reasoning = raw_text_response, "LLM call failed."
    elif raw_text_response.startswith("SYLLABUS_VERDICT: IN_SYLLABUS"):
        verdict = "IN_SYLLABUS"
        reasoning = raw_text_response.split("REASONING:", 1)[1].strip() if "REASONING:" in raw_text_response else "No reasoning from LLM."
    elif raw_text_response.startswith("SYLLABUS_VERDICT: OUT_OF_SYLLABUS"):
        verdict = "OUT_OF_SYLLABUS"
        reasoning = raw_text_response.split("REASONING:", 1)[1].strip() if "REASONING:" in raw_text_response else "No reasoning from LLM."
    else:
        reasoning = f"Unexpected syllabus response format: {raw_text_response[:200]}..."
    
    return verdict, reasoning

def check_textbook_coverage(question_details, syllabus_verdict_reasoning, retrieved_textbook_items, gemini_provider):
    """Check if a question is covered in the textbooks using Gemini"""
    q_text = question_details["question_text"]
    textbook_context_str = format_retrieved_context_for_llm(retrieved_textbook_items, "Textbook")
    
    prompt = f"""An expert academic assistant determined a question is IN_SYLLABUS. Now, check textbook coverage.
Question: "{q_text}"
Syllabus Finding: "{syllabus_verdict_reasoning[:300]}..."

{textbook_context_str}

Based ONLY on the "Relevant Textbook Sections" provided above (if any, these may come from one or more textbook files):
1. Is the question's topic substantively covered in the provided textbook excerpts?
2. Answer strictly with "TEXTBOOK_COVERAGE: YES_IN_TEXTBOOK" or "TEXTBOOK_COVERAGE: NO_IN_PROVIDED_TEXTBOOK_EXCERPTS".
3. Immediately after the verdict, on a new line, provide your reasoning starting with "REASONING: ".
   - If YES_IN_TEXTBOOK, briefly explain how and quote relevant part(s) from the textbook context, mentioning the source document if available in metadata.
   - If NO_IN_PROVIDED_TEXTBOOK_EXCERPTS, explain why (e.g., topic not found, mentioned superficially, or context insufficient).

Example YES_IN_TEXTBOOK:
TEXTBOOK_COVERAGE: YES_IN_TEXTBOOK
REASONING: The textbook excerpt from 'Operating_System_Concepts.pdf' discusses 'Process Control Block (PCB)' in detail, stating "Each process is represented in the operating system by a process control block (PCB)...".

Example NO_IN_PROVIDED_TEXTBOOK_EXCERPTS:
TEXTBOOK_COVERAGE: NO_IN_PROVIDED_TEXTBOOK_EXCERPTS
REASONING: While the textbook mentions 'scheduling' in general, the specific 'Fuzzy Logic Scheduling Algorithm' asked in the question is not detailed in the provided excerpts.
"""
    
    raw_text_response = gemini_provider.get_completion(prompt)
    verdict, reasoning = "ERROR_PARSING_LLM_RESPONSE", "Could not parse LLM response for textbook."
    
    if raw_text_response.startswith("ERROR_LLM_"):
        verdict, reasoning = raw_text_response, "LLM call failed."
    elif raw_text_response.startswith("TEXTBOOK_COVERAGE: YES_IN_TEXTBOOK"):
        verdict = "YES_IN_TEXTBOOK"
        reasoning = raw_text_response.split("REASONING:", 1)[1].strip() if "REASONING:" in raw_text_response else "No reasoning from LLM."
    elif raw_text_response.startswith("TEXTBOOK_COVERAGE: NO_IN_PROVIDED_TEXTBOOK_EXCERPTS"):
        verdict = "NO_IN_PROVIDED_TEXTBOOK_EXCERPTS"
        reasoning = raw_text_response.split("REASONING:", 1)[1].strip() if "REASONING:" in raw_text_response else "No reasoning from LLM."
    else:
        reasoning = f"Unexpected textbook response format: {raw_text_response[:200]}..."
    
    return verdict, reasoning

def normalize_unit_id(unit_id_str):
    """Normalize unit ID for consistent comparison"""
    if not unit_id_str:
        return "UNIT-UNKNOWN"
    
    normalized = unit_id_str.upper().replace(" ", "").replace("_", "")
    match = re.match(r"(UNIT)([IVXLCDM\d]+)", normalized)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    
    return normalized

def process_question_entry(unit_qp_name, q_num_qp, sub_part_key_qp, q_text_qp, syllabus_vector_store, textbook_vector_store, gemini_provider):
    """Process a single question entry and validate against syllabus and textbooks"""
    if not sub_part_key_qp:
        sub_part_key_qp = ""
    sub_part_key_qp = re.sub(r'[\W_]+', '', sub_part_key_qp)
    
    question_id_str = f"{unit_qp_name} Q{q_num_qp}{sub_part_key_qp if sub_part_key_qp else ''}"
    current_question_details = {
        "q_paper_unit": unit_qp_name,
        "q_paper_num": q_num_qp,
        "q_paper_subpart": sub_part_key_qp,
        "question_text": q_text_qp
    }
    
    result_entry = {
        "question_identifier": question_id_str,
        "question_text": q_text_qp,
        "syllabus_status": "NOT_PROCESSED",
        "syllabus_reasoning": "",
        "textbook_coverage_status": "NOT_CHECKED",
        "textbook_reasoning": "",
        "retrieved_syllabus_context_summary": [],
        "retrieved_textbook_context_summary": []
    }
    
    # Check syllabus coverage
    if not syllabus_vector_store or not syllabus_vector_store.faiss_index or syllabus_vector_store.faiss_index.ntotal == 0:
        result_entry["syllabus_status"] = "ERROR_NO_SYLLABUS_VS"
        result_entry["syllabus_reasoning"] = "Syllabus vector store not ready or empty."
    else:
        embedding_fn = lambda text: gemini_provider.get_single_embedding(text, task_type="RETRIEVAL_QUERY")
        retrieved_syllabus = syllabus_vector_store.search(q_text_qp, k=3, embedding_fn=embedding_fn)
        
        for item in retrieved_syllabus:
            result_entry["retrieved_syllabus_context_summary"].append(
                f"Dist: {item['distance']:.4f}, "
                f"Meta: {item['document'].metadata}, "
                f"Content: {item['document'].page_content[:100].replace(chr(10),' ')}..."
            )
        
        s_status, s_reasoning = check_syllabus_coverage(current_question_details, retrieved_syllabus, gemini_provider)
        result_entry["syllabus_status"], result_entry["syllabus_reasoning"] = s_status, s_reasoning
    
    # Check textbook coverage if in syllabus
    if result_entry["syllabus_status"] == "IN_SYLLABUS":
        if textbook_vector_store and textbook_vector_store.faiss_index and textbook_vector_store.faiss_index.ntotal > 0:
            embedding_fn = lambda text: gemini_provider.get_single_embedding(text, task_type="RETRIEVAL_QUERY")
            retrieved_textbook = textbook_vector_store.search(q_text_qp, k=3, embedding_fn=embedding_fn)
            
            for item in retrieved_textbook:
                result_entry["retrieved_textbook_context_summary"].append(
                    f"Dist: {item['distance']:.4f}, "
                    f"Meta: {item['document'].metadata}, "
                    f"Content: {item['document'].page_content[:100].replace(chr(10),' ')}..."
                )
            
            t_status, t_reasoning = check_textbook_coverage(
                current_question_details,
                result_entry['syllabus_reasoning'],
                retrieved_textbook,
                gemini_provider
            )
            result_entry["textbook_coverage_status"] = t_status
            result_entry["textbook_reasoning"] = t_reasoning
        else:
            result_entry["textbook_coverage_status"] = "NOT_CHECKED (Textbook VS Unavailable or Empty)"
    else:
        result_entry["textbook_coverage_status"] = "NOT_APPLICABLE (OUT_OF_SYLLABUS or SYLLABUS_ERROR)"
    
    return result_entry

def validate_question_paper(question_paper_data, syllabus_vs_path, textbook_vs_paths, gemini_api_key):
    """Validate a question paper against syllabus and textbooks"""
    gemini_provider = GeminiEmbeddingProvider(api_key=gemini_api_key)
    
    # Load the syllabus vector store
    syllabus_vector_store = SimpleVectorStoreFAISS(load_from_path=syllabus_vs_path)
    
    # Load textbook vector stores (may be multiple)
    textbook_vector_store = None
    if textbook_vs_paths:
        # For simplicity, we'll load the first one. In a more advanced version,
        # we could combine multiple textbook vector stores.
        textbook_vector_store = SimpleVectorStoreFAISS(load_from_path=textbook_vs_paths[0])
    
    # Extract course name if available
    course_name = "Unknown Course"
    if syllabus_vector_store and syllabus_vector_store.documents:
        for doc in syllabus_vector_store.documents:
            if doc.metadata.get("course_name"):
                course_name = doc.metadata.get("course_name")
                break
    
    # Initialize the results
    overall_results = {
        "course_name": course_name,
        "validation_summary": [],
        "errors_encountered": []
    }
    
    for idx, question_entry in enumerate(question_paper_data):
        question_id_field = question_entry.get("question", f"UNKNOWN_ID_IDX_{idx}")
        q_text_qp = question_entry.get("text", "")
        
        if not q_text_qp or not q_text_qp.strip():
            overall_results["errors_encountered"].append(f"Skipped question with empty text: ID '{question_id_field}'")
            continue
        
        # Parse the question ID
        unit_qp_name_str, q_num_str, sub_part_key_str = "UNKNOWN_UNIT", "0", ""
        match = re.match(r"^(.*?)\s*-\s*(\d+)([a-zA-Z]*)?$", question_id_field.strip())
        
        if match:
            unit_qp_name_str = match.group(1).strip()
            q_num_str = match.group(2)
            sub_part_key_str = match.group(3) if match.group(3) else ""
        else:
            # Fallback parsing
            parts = question_id_field.split(' - ', 1)
            if len(parts) == 2:
                unit_qp_name_str = parts[0].strip()
                num_subpart_str = parts[1].strip()
                num_match = re.match(r"(\d+)([a-zA-Z]*)", num_subpart_str)
                if num_match:
                    q_num_str, sub_part_key_str = num_match.group(1), (num_match.group(2) if num_match.group(2) else "")
                else:
                    q_num_str = re.sub(r'\D', '', num_subpart_str)
                    q_num_str = q_num_str if q_num_str else "0"
            else:
                unit_match_fallback = re.match(r"^(UNIT[\s\-IVXLCDM\d]+)", question_id_field.strip(), re.IGNORECASE)
                if unit_match_fallback:
                    unit_qp_name_str = unit_match_fallback.group(1).strip()
                num_match_fallback = re.search(r"(\d+)([a-zA-Z]*)?$", question_id_field.strip())
                if num_match_fallback:
                    q_num_str = num_match_fallback.group(1)
                    sub_part_key_str = num_match_fallback.group(2) if num_match_fallback.group(2) else ""
        
        # Normalize the unit ID
        unit_qp_name = normalize_unit_id(unit_qp_name_str)
        q_num_qp = q_num_str if q_num_str.isdigit() else "0"
        sub_part_key_qp = sub_part_key_str.lower()
        
        # Process the question entry
        result_entry = process_question_entry(
            unit_qp_name,
            q_num_qp,
            sub_part_key_qp,
            q_text_qp,
            syllabus_vector_store,
            textbook_vector_store,
            gemini_provider
        )
        
        overall_results["validation_summary"].append(result_entry)
    
    return overall_results 