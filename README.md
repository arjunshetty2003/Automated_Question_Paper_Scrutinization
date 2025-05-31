# Automated Question Paper Scrutinization System

A comprehensive web application for automated question paper validation using AI, built with Flask backend and React frontend.

## 🚀 Features

- **Admin Dashboard**: Manage subjects, upload syllabi and textbooks
- **Teacher Interface**: Upload and validate question papers
- **RAG Pipeline**: Retrieval-Augmented Generation for accurate validation
- **AI-Powered Analysis**: Using Google Gemini API for content understanding
- **Vector Search**: FAISS-based similarity search for syllabus alignment
- **PDF Processing**: Extract and analyze questions from uploaded papers
- **Real-time Validation**: Instant feedback on question paper quality

## 🏗️ Architecture

- **Backend**: Flask with modular architecture
- **Frontend**: React with Tailwind CSS
- **Database**: MongoDB Atlas for data storage
- **Vector Store**: FAISS for embeddings and similarity search
- **AI/ML**: Google Gemini API for LLM and embeddings
- **File Processing**: PDF extraction and text processing utilities

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- Google Gemini API key

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Automated_Question_Paper_Scrutinization
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/qp_scrutinization
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

Edit `.env` file:
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### 4. Database Initialization

```bash
cd backend
python scripts/init_db.py
```

This will create:
- Database indexes
- Default admin user (username: `admin`, password: `admin123`)

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

Backend will run on: http://localhost:5000

### Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:5173

## 📚 Usage Guide

### For Administrators

1. **Login** with admin credentials (admin/admin123)
2. **Create Subjects** in the admin dashboard
3. **Upload Syllabi** - Upload syllabus forms or documents
4. **Upload Textbooks** - Upload PDF textbooks for each subject
5. **Generate Embeddings** - Process documents for AI analysis

### For Teachers

1. **Register** a new account (contact admin for activation)
2. **Select Subject** from available subjects
3. **Upload Question Paper** - PDF format supported
4. **Review Results** - Get detailed validation analysis
5. **Download Reports** - Export validation results

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Admin Routes
- `GET /api/admin/subjects` - Get all subjects
- `POST /api/admin/subjects` - Create new subject
- `POST /api/admin/subjects/{id}/syllabus` - Upload syllabus
- `POST /api/admin/subjects/{id}/textbooks` - Upload textbook
- `POST /api/admin/subjects/{id}/generate-embeddings` - Generate embeddings

### User Routes
- `GET /api/user/subjects` - Get available subjects
- `POST /api/user/subjects/{id}/validate` - Validate question paper
- `POST /api/user/preview` - Preview extracted questions

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── api/                     # API routes
│   │   ├── core/                    # Core business logic
│   │   ├── db/                      # Database managers
│   │   ├── models/                  # Data models
│   │   └── utils/                   # Utility functions
│   ├── scripts/                     # Setup scripts
│   ├── config.py                    # Configuration
│   ├── run.py                       # Application entry point
│   └── requirements.txt             # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── contexts/                # React contexts
│   │   ├── services/                # API services
│   │   └── hooks/                   # Custom hooks
│   ├── public/                      # Static assets
│   └── package.json                 # Node.js dependencies
└── README.md
```

## 🔒 Security Features

- JWT-based authentication
- Role-based access control (Admin/Teacher)
- File upload validation
- CORS protection
- Password hashing with Werkzeug

## ⚡ Performance Optimizations

- Vector embeddings for fast similarity search
- Chunked document processing
- Efficient PDF text extraction
- Optimized database queries with indexes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please contact the development team or create an issue in the repository.

## 📊 System Requirements

### Development
- RAM: 8GB minimum
- Storage: 5GB free space
- Internet: Required for AI API calls

### Production
- RAM: 16GB recommended
- Storage: 50GB+ for document storage
- Database: MongoDB Atlas or self-hosted MongoDB
- CDN: Recommended for file serving

## 🚀 Deployment

### Backend Deployment (Heroku/AWS/GCP)
1. Set environment variables
2. Configure database connection
3. Upload application files
4. Run initialization script

### Frontend Deployment (Vercel/Netlify)
1. Build the application: `npm run build`
2. Deploy the dist folder
3. Configure API base URL

## 🔄 Updates and Maintenance

- Regular dependency updates
- Database backup procedures
- Log monitoring and analysis
- Performance monitoring
- Security patch management

## Tech Stack

### Backend
- Flask (Python web framework)
- MongoDB Atlas (Database)
- FAISS (Vector similarity search)
- Google Gemini API (LLM and embeddings)
- PyMongo (MongoDB driver)
- pdfplumber (PDF processing)

### Frontend
- React with Vite
- Tailwind CSS (Styling)
- Axios (API client)
- React Router (Navigation)

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   └── utils/
│   ├── instance/
│   ├── config.py
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── public/
└── README.md
```

## Getting Started

### Backend Setup
1. Navigate to backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables in `.env`
4. Run Flask app: `python run.py`

### Frontend Setup
1. Navigate to frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`

## Environment Variables

Create a `.env` file in the backend directory:

```
GEMINI_API_KEY=your_gemini_api_key
MONGO_DB_URI=your_mongodb_atlas_uri
SECRET_KEY=your_secret_key
FLASK_ENV=development
```

## API Endpoints

### Admin Routes
- `POST /api/admin/subjects` - Create new subject
- `GET /api/admin/subjects` - List all subjects
- `DELETE /api/admin/subjects/<id>` - Delete subject
- `POST /api/admin/subjects/<id>/syllabus` - Upload syllabus
- `POST /api/admin/subjects/<id>/textbooks` - Upload textbooks

### User Routes
- `GET /api/subjects` - Get subjects list
- `POST /api/validate/question-paper/<id>` - Validate question paper

## License

MIT License
