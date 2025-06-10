# RAG Question Paper Validation System

A simplified web application for automated question paper validation using AI, built with Flask backend and React frontend.

## Features

- **Subject Management**: Create and manage academic subjects
- **Syllabus Upload**: Upload detailed syllabus information for each subject
- **Textbook Processing**: Upload and process PDF textbooks
- **Question Paper Validation**: AI-powered validation of question papers against syllabus and textbooks
- **Real-time Analysis**: Instant feedback with detailed scoring and recommendations

## Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API key (hardcoded in the application)

## Installation & Setup

### 1. Clone and Navigate
```bash
cd /Users/arjun/Documents/Automated_Question_Paper_Scrutinization/simple_app
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create uploads directory
mkdir uploads

# Run the Flask server
python app.py
```

Backend will run on: http://localhost:5001

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on: http://localhost:5173

## Usage Guide

### 1. Create Subjects
- Navigate to "Manage Subjects" tab
- Enter subject name (e.g., "Operating Systems")
- Click "Create Subject"

### 2. Upload Syllabus
- Select a subject from the dropdown
- Go to "Upload Syllabus" tab
- Add course name and units with detailed content
- Click "Upload Syllabus"

### 3. Upload Textbooks
- Go to "Upload Textbooks" tab
- Drag and drop PDF files or click to upload
- Wait for processing to complete

### 4. Validate Question Papers
- Go to "Validate Papers" tab
- Upload a question paper PDF
- Click "Validate Question Paper"
- Review detailed analysis results

## Technical Details

### Backend (Flask)
- **No Database**: Uses in-memory storage
- **PDF Processing**: pdfplumber for text extraction
- **AI Integration**: Google Gemini for LLM and embeddings
- **Vector Search**: FAISS for similarity search
- **CORS Enabled**: For frontend communication

### Frontend (React)
- **Tailwind CSS**: For styling
- **Axios**: For API communication
- **File Upload**: Drag & drop support
- **Real-time**: Live validation results

### API Endpoints

- `GET /api/subjects` - Get all subjects
- `POST /api/subjects` - Create new subject
- `POST /api/subjects/{name}/syllabus` - Upload syllabus
- `POST /api/subjects/{name}/textbooks` - Upload textbooks
- `POST /api/validate/{name}` - Validate question paper

## Configuration

The Gemini API key is hardcoded in `backend/app.py`:
```python
GEMINI_API_KEY = "AIzaSyDq2pu2wM0FnBgNePLzzkXshap0A5-zAv0"
```

## File Structure

```
simple_app/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── uploads/           # File storage directory
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   ├── package.json       # Node dependencies
│   └── index.html         # HTML template
└── README.md              # This file
```

## Limitations

- **In-Memory Storage**: Data is lost when server restarts
- **File Storage**: Files stored locally in uploads/ directory
- **Single Instance**: Not designed for production deployment
- **No Authentication**: Open access to all features

## Troubleshooting

1. **Backend won't start**: Check Python version and virtual environment
2. **Frontend build errors**: Ensure Node.js version is 16+
3. **API errors**: Verify Gemini API key is valid
4. **File upload fails**: Check file size (16MB limit) and format (PDF only)

## Development

To modify or extend the application:

1. **Backend**: Edit `backend/app.py` for API changes
2. **Frontend**: Modify components in `frontend/src/components/`
3. **Styling**: Update Tailwind classes or `frontend/src/index.css`
4. **API Integration**: Update `frontend/src/services/api.js`

## License

This project is for educational purposes.
