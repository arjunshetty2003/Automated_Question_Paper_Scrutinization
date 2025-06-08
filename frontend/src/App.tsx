import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import SyllabusUpload from './pages/SyllabusUpload';
import TextbookUpload from './pages/TextbookUpload';
import QuestionPaperUpload from './pages/QuestionPaperUpload';
import ValidationResults from './pages/ValidationResults';
import NotFound from './pages/NotFound';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload-syllabus" element={<SyllabusUpload />} />
            <Route path="/upload-textbook" element={<TextbookUpload />} />
            <Route path="/upload-question-paper" element={<QuestionPaperUpload />} />
            <Route path="/results/:resultId" element={<ValidationResults />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App; 