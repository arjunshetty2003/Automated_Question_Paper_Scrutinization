import React, { useState, useEffect } from 'react';
import { apiService } from './services/api';
import SyllabusUploader from './components/SyllabusUploader';
import TextbookUploader from './components/TextbookUploader';
import QuestionPaperValidator from './components/QuestionPaperValidator';
import Alert from './components/Alert';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [newSubjectName, setNewSubjectName] = useState('');
  const [currentTab, setCurrentTab] = useState('subjects');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      setLoading(true);
      const data = await apiService.getSubjects();
      setSubjects(data.subjects || []);
    } catch (error) {
      setError('Failed to fetch subjects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSubject = async (e) => {
    e.preventDefault();
    if (!newSubjectName.trim()) return;

    try {
      await apiService.createSubject(newSubjectName.trim());
      setNewSubjectName('');
      fetchSubjects();
      setSelectedSubject(newSubjectName.trim());
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to create subject');
    }
  };

  const tabs = [
    { id: 'subjects', label: 'Subjects', icon: '📚' },
    { id: 'syllabus', label: 'Syllabus', icon: '📋', disabled: !selectedSubject },
    { id: 'textbooks', label: 'Textbooks', icon: '📖', disabled: !selectedSubject },
    { id: 'validate', label: 'Validate', icon: '✅', disabled: !selectedSubject },
  ];

  if (loading && subjects.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                RAG Question Paper Validator
              </h1>
              <p className="text-sm text-gray-600">
                AI-powered question paper validation system
              </p>
            </div>
            
            {/* Subject Selector */}
            {subjects.length > 0 && (
              <div className="flex items-center space-x-4">
                <label htmlFor="subject-select" className="text-sm font-medium text-gray-700">
                  Current Subject:
                </label>
                <select
                  id="subject-select"
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="input-field min-w-48"
                >
                  <option value="">Select a subject...</option>
                  {subjects.map((subject) => (
                    <option key={subject} value={subject}>
                      {subject}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => !tab.disabled && setCurrentTab(tab.id)}
                disabled={tab.disabled}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  currentTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : tab.disabled
                    ? 'border-transparent text-gray-400 cursor-not-allowed'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <Alert
            type="error"
            message={error}
            onClose={() => setError('')}
            className="mb-6"
          />
        )}

        {/* Tab Content */}
        <div className="space-y-6">
          {currentTab === 'subjects' && (
            <div className="space-y-6">
              {/* Create Subject Form */}
              <div className="card">
                <div className="card-header">
                  <h2 className="text-xl font-semibold text-secondary-900">Create New Subject</h2>
                </div>
                <div className="card-body">
                  <form onSubmit={handleCreateSubject} className="flex space-x-4">
                    <input
                      type="text"
                      value={newSubjectName}
                      onChange={(e) => setNewSubjectName(e.target.value)}
                      className="input-field flex-1"
                      placeholder="Enter subject name (e.g., Operating Systems)"
                      required
                    />
                    <button type="submit" className="btn-primary">
                      Create Subject
                    </button>
                  </form>
                </div>
              </div>

              {/* Available Subjects */}
              {subjects.length > 0 && (
                <div className="card">
                  <div className="card-header">
                    <h2 className="text-xl font-semibold text-secondary-900">Available Subjects</h2>
                  </div>
                  <div className="card-body">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {subjects.map((subject) => (
                        <div
                          key={subject}
                          className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                            selectedSubject === subject
                              ? 'border-primary-500 bg-primary-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => setSelectedSubject(subject)}
                        >
                          <h3 className="font-medium text-gray-900">{subject}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {selectedSubject === subject ? 'Selected' : 'Click to select'}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {currentTab === 'syllabus' && selectedSubject && (
            <SyllabusUploader subjectName={selectedSubject} />
          )}

          {currentTab === 'textbooks' && selectedSubject && (
            <TextbookUploader subjectName={selectedSubject} />
          )}

          {currentTab === 'validate' && selectedSubject && (
            <QuestionPaperValidator subjectName={selectedSubject} />
          )}

          {/* Welcome Message */}
          {!selectedSubject && currentTab !== 'subjects' && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No subject selected</h3>
              <p className="mt-1 text-sm text-gray-500">
                Please select a subject to continue with {currentTab}.
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>RAG Question Paper Validation System</p>
            <p className="mt-1">Powered by Google Gemini AI</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
