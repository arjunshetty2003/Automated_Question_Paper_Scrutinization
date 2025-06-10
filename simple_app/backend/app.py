from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import time
import re
import numpy as np

import google.generativeai as genai
import pdfplumber
import faiss

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Hardcoded Gemini API Key
GEMINI_API_KEY = "AIzaSyDq2pu2wM0FnBgNePLzzkXshap0A5-zAv0"
EMBEDDING_MODEL_NAME = "models/text-embedding-004"
GENERATIVE_MODEL_NAME = 'gemini-1.5-flash-latest'
LLM_CALL_DELAY_SECONDS = 2

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
GENERATIVE_MODEL_INSTANCE = genai.GenerativeModel(GENERATIVE_MODEL_NAME)

# Global variables for storing data (in-memory storage)
subjects_data = {}
vector_stores = {}

class SimpleDocument:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}
    
    def __repr__(self):
        return f"SimpleDocument(page_content='{self.page_content[:50].replace(chr(10), ' ')}...', metadata={self.metadata})"

class SimpleVectorStoreFAISS:
    def __init__(self, documents, embeddings_list):
        self.documents = []
        self.faiss_index = None
        self.dimension = 0
        
        # Filter out None embeddings and corresponding documents
        valid_docs = []
        valid_embeddings = []
        
        for doc, embedding in zip(documents, embeddings_list):
            if embedding is not None:
                valid_docs.append(doc)
                valid_embeddings.append(embedding)
        
        if valid_embeddings:
            self.documents = valid_docs
            embeddings_array = np.array(valid_embeddings, dtype='float32')
            self.dimension = embeddings_array.shape[1]
            
            # Create FAISS index
            self.faiss_index = faiss.IndexFlatL2(self.dimension)
            self.faiss_index.add(embeddings_array)
    
    def search(self, query_text, k=3):
        if not self.faiss_index or not query_text:
            return []
        
        try:
            # Get query embedding
            query_embedding = get_gemini_embeddings([query_text], task_type="RETRIEVAL_QUERY")
            if not query_embedding or query_embedding[0] is None:
                return []
            
            query_vector = np.array([query_embedding[0]], dtype='float32')
            
            # Search
            distances, indices = self.faiss_index.search(query_vector, min(k, len(self.documents)))
            
            retrieved_docs = []
            if len(indices) > 0:
                for i, idx in enumerate(indices[0]):
                    if idx != -1 and idx < len(self.documents):
                        retrieved_docs.append({
                            "document": self.documents[idx], 
                            "distance": float(distances[0][i])
                        })
            return retrieved_docs
        except Exception as e:
            print(f"Error searching: {e}")
            return []

def chunk_text_by_paragraphs(text, min_chunk_len=50, max_chunk_len=700):
    """Split text into chunks based on paragraphs."""
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
        elif len(current_chunk) + len(para) + 1 <= max_chunk_len:
            current_chunk += "\n\n" + para
        else:
            if len(current_chunk) >= min_chunk_len:
                chunks.append(current_chunk)
            current_chunk = para
    
    if current_chunk and len(current_chunk) >= min_chunk_len:
        chunks.append(current_chunk)
    
    return chunks

def get_gemini_embeddings(texts, task_type="RETRIEVAL_DOCUMENT"):
    """Get embeddings from Gemini API."""
    if not texts:
        return []
    
    embeddings_list = []
    BATCH_SIZE = 100
    
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        valid_texts = [text for text in batch_texts if text and text.strip()]
        
        if not valid_texts:
            embeddings_list.extend([None] * len(batch_texts))
            continue
        
        try:
            response = genai.embed_content(
                model=EMBEDDING_MODEL_NAME,
                content=valid_texts,
                task_type=task_type
            )
            
            batch_embeddings = response['embedding'] if 'embedding' in response else []
            
            # Handle single text case
            if len(valid_texts) == 1 and not isinstance(batch_embeddings[0], list):
                batch_embeddings = [batch_embeddings]
            
            embeddings_list.extend(batch_embeddings)
            
            # Rate limiting
            time.sleep(LLM_CALL_DELAY_SECONDS)
            
        except Exception as e:
            print(f"Error getting embeddings for batch: {e}")
            embeddings_list.extend([None] * len(batch_texts))
    
    return embeddings_list

def extract_text_from_pdf(file_path):
    """Extract text from PDF file."""
    try:
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_content.append({
                        "page": page_num + 1,
                        "text": text.strip()
                    })
        return text_content
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return []

def check_syllabus_coverage_with_gemini(question_text, syllabus_context, question_id):
    """Check if question is covered by syllabus using Gemini."""
    prompt = f"""
    Question ID: {question_id}
    Question: {question_text}
    
    Relevant Syllabus Content:
    {syllabus_context}
    
    Please analyze if this question is covered by the provided syllabus content. Provide:
    1. A coverage score from 0-100 (where 100 means fully covered)
    2. A brief explanation of coverage
    3. Specific syllabus topics that relate to this question
    
    Format your response as JSON:
    {{
        "coverage_score": <score>,
        "explanation": "<explanation>",
        "related_topics": ["<topic1>", "<topic2>"]
    }}
    """
    
    try:
        response = GENERATIVE_MODEL_INSTANCE.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response
        if result_text.startswith('```json'):
            result_text = result_text[7:-3]
        elif result_text.startswith('```'):
            result_text = result_text[3:-3]
        
        return json.loads(result_text)
    except Exception as e:
        print(f"Error in syllabus coverage check: {e}")
        return {
            "coverage_score": 0,
            "explanation": f"Error analyzing coverage: {str(e)}",
            "related_topics": []
        }

def check_textbook_alignment_with_gemini(question_text, textbook_context, question_id):
    """Check if question aligns with textbook content using Gemini."""
    prompt = f"""
    Question ID: {question_id}
    Question: {question_text}
    
    Relevant Textbook Content:
    {textbook_context}
    
    Please analyze if this question aligns with the provided textbook content. Provide:
    1. An alignment score from 0-100 (where 100 means perfectly aligned)
    2. A brief explanation of alignment
    3. Specific textbook sections that relate to this question
    
    Format your response as JSON:
    {{
        "alignment_score": <score>,
        "explanation": "<explanation>",
        "related_sections": ["<section1>", "<section2>"]
    }}
    """
    
    try:
        response = GENERATIVE_MODEL_INSTANCE.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response
        if result_text.startswith('```json'):
            result_text = result_text[7:-3]
        elif result_text.startswith('```'):
            result_text = result_text[3:-3]
        
        return json.loads(result_text)
    except Exception as e:
        print(f"Error in textbook alignment check: {e}")
        return {
            "alignment_score": 0,
            "explanation": f"Error analyzing alignment: {str(e)}",
            "related_sections": []
        }

# API Routes

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get all subjects."""
    return jsonify(list(subjects_data.keys()))

@app.route('/api/subjects', methods=['POST'])
def create_subject():
    """Create a new subject."""
    data = request.get_json()
    subject_name = data.get('subject_name', '').strip()
    
    if not subject_name:
        return jsonify({"error": "Subject name is required"}), 400
    
    if subject_name in subjects_data:
        return jsonify({"error": "Subject already exists"}), 400
    
    subjects_data[subject_name] = {
        "syllabus": None,
        "textbooks": []
    }
    
    return jsonify({"message": f"Subject '{subject_name}' created successfully"})

@app.route('/api/subjects/<subject_name>/syllabus', methods=['POST'])
def upload_syllabus(subject_name):
    """Upload syllabus for a subject."""
    if subject_name not in subjects_data:
        return jsonify({"error": "Subject not found"}), 404
    
    data = request.get_json()
    course_name = data.get('course_name', subject_name)
    units = data.get('units', [])
    
    if not units:
        return jsonify({"error": "Syllabus units are required"}), 400
    
    # Process syllabus for embedding
    syllabus_docs = []
    for unit_data in units:
        unit_id = unit_data.get('unit', 'Unknown Unit')
        unit_title = unit_data.get('title', 'Untitled')
        content = unit_data.get('syllabus_content', '').strip()
        
        if content:
            chunks = chunk_text_by_paragraphs(content, min_chunk_len=50, max_chunk_len=400)
            for i, chunk in enumerate(chunks):
                doc = SimpleDocument(
                    page_content=chunk,
                    metadata={
                        "source_type": "syllabus",
                        "course_name": course_name,
                        "unit_id": unit_id,
                        "unit_title": unit_title,
                        "chunk_id": f"syl_chunk_{unit_id}_{i}"
                    }
                )
                syllabus_docs.append(doc)
    
    # Generate embeddings
    if syllabus_docs:
        texts = [doc.page_content for doc in syllabus_docs]
        embeddings = get_gemini_embeddings(texts)
        
        # Create vector store
        vector_store = SimpleVectorStoreFAISS(syllabus_docs, embeddings)
        
        if subject_name not in vector_stores:
            vector_stores[subject_name] = {}
        vector_stores[subject_name]['syllabus'] = vector_store
    
    subjects_data[subject_name]['syllabus'] = {
        "course_name": course_name,
        "units": units
    }
    
    return jsonify({
        "message": "Syllabus uploaded successfully",
        "documents_created": len(syllabus_docs)
    })

@app.route('/api/subjects/<subject_name>/textbooks', methods=['POST'])
def upload_textbook(subject_name):
    """Upload textbook PDF files for a subject."""
    if subject_name not in subjects_data:
        return jsonify({"error": "Subject not found"}), 404
    
    if 'files' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No files selected"}), 400
    
    # Validate file types
    pdf_files = []
    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            pdf_files.append(file)
    
    if not pdf_files:
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    # Process textbook PDFs for embedding
    textbook_docs = []
    uploaded_files = []
    
    for file in pdf_files:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"textbook_{filename}")
        file.save(filepath)
        
        try:
            # Extract text from PDF
            pages_data = extract_text_from_pdf(filepath)
            if not pages_data:
                continue
            
            uploaded_files.append({"filename": filename, "pages": len(pages_data)})
            
            # Combine all pages text
            full_text = "\n\n".join([page["text"] for page in pages_data])
            
            # Create chunks from the extracted text
            chunks = chunk_text_by_paragraphs(full_text, min_chunk_len=50, max_chunk_len=600)
            
            for i, chunk in enumerate(chunks):
                doc = SimpleDocument(
                    page_content=chunk,
                    metadata={
                        "source_type": "textbook",
                        "filename": filename,
                        "chunk_id": f"tb_chunk_{filename}_{i}"
                    }
                )
                textbook_docs.append(doc)
        
        except Exception as e:
            print(f"Error processing PDF {filename}: {e}")
            continue
        
        finally:
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass
    
    if not textbook_docs:
        return jsonify({"error": "No text could be extracted from the uploaded PDFs"}), 400
    
    # Generate embeddings
    texts = [doc.page_content for doc in textbook_docs]
    embeddings = get_gemini_embeddings(texts)
    
    # Create vector store
    vector_store = SimpleVectorStoreFAISS(textbook_docs, embeddings)
    
    if subject_name not in vector_stores:
        vector_stores[subject_name] = {}
    vector_stores[subject_name]['textbook'] = vector_store
    
    subjects_data[subject_name]['textbooks'].extend(uploaded_files)
    
    return jsonify({
        "message": f"{len(uploaded_files)} textbook(s) uploaded successfully",
        "uploaded_files": uploaded_files,
        "documents_created": len(textbook_docs)
    })

@app.route('/api/validate-json/<subject_name>', methods=['POST'])
def validate_question_paper_json(subject_name):
    """Validate questions provided in JSON format."""
    if subject_name not in subjects_data:
        return jsonify({"error": "Subject not found"}), 404
    
    data = request.get_json()
    questions = data.get('questions', [])
    
    if not questions:
        return jsonify({"error": "No questions provided"}), 400
    
    try:
        # Validate questions directly from JSON
        validation_results = []
        syllabus_store = vector_stores.get(subject_name, {}).get('syllabus')
        textbook_store = vector_stores.get(subject_name, {}).get('textbook')
        
        for question_entry in questions:
            question_text = question_entry.get('text', '')
            question_id = question_entry.get('question', '')
            
            if not question_text:
                continue
            
            result = {
                "question_id": question_id,
                "question_text": question_text,
                "syllabus_validation": None,
                "textbook_validation": None,
                "overall_score": 0
            }
            
            # Check syllabus coverage
            syllabus_score = 0
            if syllabus_store:
                syllabus_results = syllabus_store.search(question_text, k=3)
                syllabus_context = "\n\n".join([
                    item["document"].page_content for item in syllabus_results
                ])
                
                if syllabus_context:
                    result["syllabus_validation"] = check_syllabus_coverage_with_gemini(
                        question_text, syllabus_context, question_id
                    )
                    syllabus_score = result["syllabus_validation"].get("coverage_score", 0)
            
            # Check textbook alignment
            textbook_score = 0
            if textbook_store:
                textbook_results = textbook_store.search(question_text, k=3)
                textbook_context = "\n\n".join([
                    item["document"].page_content for item in textbook_results
                ])
                
                if textbook_context:
                    result["textbook_validation"] = check_textbook_alignment_with_gemini(
                        question_text, textbook_context, question_id
                    )
                    textbook_score = result["textbook_validation"].get("alignment_score", 0)
            
            # Calculate overall score
            result["overall_score"] = (syllabus_score + textbook_score) / 2
            
            validation_results.append(result)
        
        # Calculate summary
        total_questions = len(validation_results)
        avg_score = sum(r["overall_score"] for r in validation_results) / total_questions if total_questions > 0 else 0
        
        return jsonify({
            "success": True,
            "subject_name": subject_name,
            "total_questions": total_questions,
            "average_score": avg_score,
            "questions": questions,
            "validation_results": validation_results
        })
    
    except Exception as e:
        return jsonify({"error": f"Validation failed: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "subjects_count": len(subjects_data),
        "vector_stores_count": len(vector_stores)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
