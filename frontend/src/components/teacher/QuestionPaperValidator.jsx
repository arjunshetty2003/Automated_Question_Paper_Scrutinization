import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { userService } from '../../services/userService';
import LoadingSpinner from '../common/LoadingSpinner';
import Alert from '../common/Alert';

const QuestionPaperValidator = () => {
  const [searchParams] = useSearchParams();
  const preselectedSubject = searchParams.get('subject');

  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(preselectedSubject || '');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      setLoading(true);
      const data = await userService.getSubjects();
      const availableSubjects = (data.subjects || []).filter(
        s => s.syllabusUploaded && s.textbooksCount > 0 && s.embeddingsGenerated
      );
      setSubjects(availableSubjects);
    } catch (error) {
      setError('Failed to fetch subjects');
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
        setError('');
      } else {
        setError('Please upload a PDF file only');
      }
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Please upload a PDF file only');
      }
    }
  };

  const handleValidate = async () => {
    if (!selectedSubject || !file) {
      setError('Please select a subject and upload a question paper');
      return;
    }

    setValidating(true);
    setError('');
    setResults(null);

    try {
      const formData = new FormData();
      formData.append('question_paper', file);

      const data = await userService.validateQuestionPaper(selectedSubject, formData);
      setResults(data);
    } catch (error) {
      setError(error.response?.data?.message || 'Validation failed. Please try again.');
    } finally {
      setValidating(false);
    }
  };

  const handlePreview = async () => {
    if (!file) {
      setError('Please upload a question paper first');
      return;
    }

    setValidating(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('question_paper', file);

      const data = await userService.previewQuestionPaper(formData);
      setResults({ preview: true, ...data });
    } catch (error) {
      setError(error.response?.data?.message || 'Preview failed. Please try again.');
    } finally {
      setValidating(false);
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
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900">Question Paper Validator</h1>
        <p className="mt-2 text-secondary-600">
          Upload a question paper PDF to validate against syllabus and textbooks
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="space-y-6">
          <div className="card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-secondary-900">Upload Question Paper</h2>
            </div>
            <div className="card-body space-y-4">
              {/* Subject Selection */}
              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-secondary-700 mb-2">
                  Select Subject
                </label>
                <select
                  id="subject"
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="input-field"
                >
                  <option value="">Choose a subject...</option>
                  {subjects.map((subject) => (
                    <option key={subject._id} value={subject._id}>
                      {subject.name} ({subject.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Question Paper PDF
                </label>
                <div
                  className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                    dragActive
                      ? 'border-primary-400 bg-primary-50'
                      : file
                      ? 'border-green-400 bg-green-50'
                      : 'border-secondary-300 hover:border-secondary-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  {file ? (
                    <div className="space-y-2">
                      <svg className="mx-auto h-12 w-12 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div className="text-sm font-medium text-green-700">{file.name}</div>
                      <div className="text-xs text-green-600">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                      <button
                        onClick={() => setFile(null)}
                        className="text-xs text-red-600 hover:text-red-800"
                      >
                        Remove file
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <svg className="mx-auto h-12 w-12 text-secondary-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      <div className="text-sm text-secondary-600">
                        <label htmlFor="file-upload" className="cursor-pointer">
                          <span className="text-primary-600 font-medium hover:text-primary-500">
                            Click to upload
                          </span>
                          <span> or drag and drop</span>
                        </label>
                        <input
                          id="file-upload"
                          name="file-upload"
                          type="file"
                          accept=".pdf"
                          className="sr-only"
                          onChange={handleFileSelect}
                        />
                      </div>
                      <p className="text-xs text-secondary-500">PDF files only, up to 10MB</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-4">
                <button
                  onClick={handlePreview}
                  disabled={!file || validating}
                  className="btn-secondary flex-1"
                >
                  {validating ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Processing...
                    </>
                  ) : (
                    'Preview Questions'
                  )}
                </button>
                <button
                  onClick={handleValidate}
                  disabled={!selectedSubject || !file || validating}
                  className="btn-primary flex-1"
                >
                  {validating ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Validating...
                    </>
                  ) : (
                    'Validate Paper'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div>
          {results ? (
            <div className="space-y-6">
              {results.preview ? (
                <div className="card">
                  <div className="card-header">
                    <h2 className="text-xl font-semibold text-secondary-900">Extracted Questions</h2>
                  </div>
                  <div className="card-body">
                    {results.questions && results.questions.length > 0 ? (
                      <div className="space-y-4">
                        {results.questions.map((question, index) => (
                          <div key={index} className="border-l-4 border-primary-400 pl-4 py-2">
                            <div className="text-sm font-medium text-secondary-700 mb-1">
                              Question {index + 1}
                            </div>
                            <div className="text-secondary-900">{question}</div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-secondary-500">
                        No questions could be extracted from the PDF
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <>
                  {/* Validation Results */}
                  <div className="card">
                    <div className="card-header">
                      <h2 className="text-xl font-semibold text-secondary-900">Validation Results</h2>
                    </div>
                    <div className="card-body">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div className="text-center p-4 bg-primary-50 rounded-lg">
                          <div className="text-2xl font-bold text-primary-600">
                            {results.overall_score ? `${Math.round(results.overall_score * 100)}%` : 'N/A'}
                          </div>
                          <div className="text-sm text-primary-700">Overall Score</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">
                            {results.syllabus_coverage ? `${Math.round(results.syllabus_coverage * 100)}%` : 'N/A'}
                          </div>
                          <div className="text-sm text-green-700">Syllabus Coverage</div>
                        </div>
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">
                            {results.questions ? results.questions.length : 0}
                          </div>
                          <div className="text-sm text-blue-700">Questions Found</div>
                        </div>
                      </div>

                      {results.validation_summary && (
                        <div className="mb-6">
                          <h3 className="text-lg font-semibold text-secondary-900 mb-3">Summary</h3>
                          <div className="bg-secondary-50 p-4 rounded-lg">
                            <p className="text-secondary-700">{results.validation_summary}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Question Analysis */}
                  {results.question_analysis && results.question_analysis.length > 0 && (
                    <div className="card">
                      <div className="card-header">
                        <h2 className="text-xl font-semibold text-secondary-900">Question Analysis</h2>
                      </div>
                      <div className="card-body">
                        <div className="space-y-4">
                          {results.question_analysis.map((analysis, index) => (
                            <div key={index} className="border rounded-lg p-4">
                              <div className="mb-3">
                                <div className="text-sm font-medium text-secondary-700 mb-1">
                                  Question {index + 1}
                                </div>
                                <div className="text-secondary-900 mb-2">{analysis.question}</div>
                                <div className="flex items-center space-x-4">
                                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    analysis.alignment_score > 0.7
                                      ? 'bg-green-100 text-green-800'
                                      : analysis.alignment_score > 0.4
                                      ? 'bg-yellow-100 text-yellow-800'
                                      : 'bg-red-100 text-red-800'
                                  }`}>
                                    {Math.round(analysis.alignment_score * 100)}% Aligned
                                  </span>
                                  {analysis.syllabus_topics && analysis.syllabus_topics.length > 0 && (
                                    <span className="text-xs text-secondary-600">
                                      Topics: {analysis.syllabus_topics.join(', ')}
                                    </span>
                                  )}
                                </div>
                              </div>
                              {analysis.feedback && (
                                <div className="text-sm text-secondary-600 bg-secondary-50 p-3 rounded">
                                  {analysis.feedback}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  {results.recommendations && results.recommendations.length > 0 && (
                    <div className="card">
                      <div className="card-header">
                        <h2 className="text-xl font-semibold text-secondary-900">Recommendations</h2>
                      </div>
                      <div className="card-body">
                        <ul className="space-y-2">
                          {results.recommendations.map((recommendation, index) => (
                            <li key={index} className="flex items-start">
                              <svg className="w-5 h-5 text-blue-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                              </svg>
                              <span className="text-secondary-700">{recommendation}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="card">
              <div className="card-body text-center py-12">
                <svg className="mx-auto h-12 w-12 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-secondary-900">No validation results yet</h3>
                <p className="mt-1 text-sm text-secondary-500">
                  Upload a question paper and select a subject to get started
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuestionPaperValidator;
