import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { userService } from '../../services/userService';
import LoadingSpinner from '../common/LoadingSpinner';
import Alert from '../common/Alert';

const TeacherDashboard = () => {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const data = await userService.getSubjects();
      setSubjects(data.subjects || []);
    } catch (error) {
      setError('Failed to fetch subjects');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900">Teacher Dashboard</h1>
        <p className="mt-2 text-secondary-600">
          Upload and validate question papers against syllabus and textbooks
        </p>
      </div>

      {error && (
        <Alert
          type="error"
          message={error}
          onClose={() => setError('')}
          className="mb-6"
        />
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Link
          to="/validate"
          className="card card-body hover:shadow-lg transition-shadow cursor-pointer bg-primary-50 border-primary-200"
        >
          <div className="flex items-center">
            <div className="bg-primary-600 p-3 rounded-lg text-white mr-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary-900">Validate Question Paper</h3>
              <p className="text-primary-700">Upload and analyze a question paper</p>
            </div>
          </div>
        </Link>

        <div className="card card-body bg-secondary-50">
          <div className="flex items-center">
            <div className="bg-secondary-600 p-3 rounded-lg text-white mr-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-secondary-900">Available Subjects</h3>
              <p className="text-2xl font-bold text-secondary-700">{subjects.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Available Subjects */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-secondary-900">Available Subjects for Validation</h2>
        </div>
        <div className="card-body">
          {subjects.length === 0 ? (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-secondary-900">No subjects available</h3>
              <p className="mt-1 text-sm text-secondary-500">
                Contact your administrator to set up subjects for question paper validation.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {subjects.map((subject) => (
                <div key={subject._id} className="card border-2 hover:border-primary-300 transition-colors">
                  <div className="card-body">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-secondary-900 mb-1">
                          {subject.name}
                        </h3>
                        <p className="text-sm text-secondary-600 mb-2">{subject.code}</p>
                        <p className="text-sm text-secondary-700 mb-4">
                          {subject.description}
                        </p>
                        
                        <div className="space-y-2 mb-4">
                          <div className="flex items-center text-sm">
                            <svg className={`w-4 h-4 mr-2 ${subject.syllabusUploaded ? 'text-green-500' : 'text-red-500'}`} fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d={subject.syllabusUploaded ? "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" : "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"} clipRule="evenodd" />
                            </svg>
                            <span className={subject.syllabusUploaded ? 'text-green-700' : 'text-red-700'}>
                              Syllabus {subject.syllabusUploaded ? 'Available' : 'Not Available'}
                            </span>
                          </div>
                          
                          <div className="flex items-center text-sm">
                            <svg className={`w-4 h-4 mr-2 ${subject.textbooksCount > 0 ? 'text-green-500' : 'text-red-500'}`} fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d={subject.textbooksCount > 0 ? "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" : "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"} clipRule="evenodd" />
                            </svg>
                            <span className={subject.textbooksCount > 0 ? 'text-green-700' : 'text-red-700'}>
                              {subject.textbooksCount || 0} Textbook(s)
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        subject.syllabusUploaded && subject.textbooksCount > 0 && subject.embeddingsGenerated
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {subject.syllabusUploaded && subject.textbooksCount > 0 && subject.embeddingsGenerated
                          ? 'Ready'
                          : 'Setup Required'}
                      </span>
                    </div>
                    
                    <div className="mt-4">
                      {subject.syllabusUploaded && subject.textbooksCount > 0 && subject.embeddingsGenerated ? (
                        <Link
                          to={`/validate?subject=${subject._id}`}
                          className="btn-primary w-full text-center"
                        >
                          Validate Question Paper
                        </Link>
                      ) : (
                        <button
                          disabled
                          className="btn-secondary w-full text-center cursor-not-allowed opacity-50"
                        >
                          Setup Required
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity Section */}
      <div className="mt-8 card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-secondary-900">Quick Start Guide</h2>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="bg-primary-100 rounded-full p-2 mr-4">
                <span className="text-primary-600 font-bold">1</span>
              </div>
              <div>
                <h4 className="font-medium text-secondary-900">Select a Subject</h4>
                <p className="text-sm text-secondary-600">Choose a subject that has syllabus and textbooks uploaded by the admin.</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-primary-100 rounded-full p-2 mr-4">
                <span className="text-primary-600 font-bold">2</span>
              </div>
              <div>
                <h4 className="font-medium text-secondary-900">Upload Question Paper</h4>
                <p className="text-sm text-secondary-600">Upload your question paper PDF for validation against the syllabus and textbooks.</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-primary-100 rounded-full p-2 mr-4">
                <span className="text-primary-600 font-bold">3</span>
              </div>
              <div>
                <h4 className="font-medium text-secondary-900">Review Results</h4>
                <p className="text-sm text-secondary-600">Get detailed analysis including syllabus coverage, question alignment, and improvement suggestions.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;
