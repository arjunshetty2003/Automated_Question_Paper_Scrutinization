import React, { useState } from 'react';
import { apiService } from '../services/api';
import Alert from './Alert';
import LoadingSpinner from './LoadingSpinner';

const QuestionPaperValidator = ({ subjectName }) => {
  const [file, setFile] = useState(null);
  const [jsonData, setJsonData] = useState('');
  const [uploadMode, setUploadMode] = useState('json'); // 'json' or 'file'
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.json')) {
      setFile(selectedFile);
      setMessage('');
      // Read JSON file content
      const reader = new FileReader();
      reader.onload = (e) => {
        setJsonData(e.target.result);
      };
      reader.readAsText(selectedFile);
    } else {
      setMessage('Please select a JSON file');
      setMessageType('error');
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
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith('.json')) {
      setFile(droppedFile);
      setMessage('');
      // Read JSON file content
      const reader = new FileReader();
      reader.onload = (e) => {
        setJsonData(e.target.result);
      };
      reader.readAsText(droppedFile);
    } else {
      setMessage('Please select a JSON file');
      setMessageType('error');
    }
  };

  const handleValidate = async (e) => {
    e.preventDefault();
    
    let questionsData;
    
    if (uploadMode === 'json') {
      if (!jsonData.trim()) {
        setMessage('Please enter question paper JSON data');
        setMessageType('error');
        return;
      }
      
      try {
        questionsData = JSON.parse(jsonData);
      } catch (error) {
        setMessage('Invalid JSON format. Please check your data.');
        setMessageType('error');
        return;
      }
    } else {
      if (!file) {
        setMessage('Please select a question paper JSON file');
        setMessageType('error');
        return;
      }
      
      try {
        questionsData = JSON.parse(jsonData);
      } catch (error) {
        setMessage('Invalid JSON file format');
        setMessageType('error');
        return;
      }
    }

    setLoading(true);
    setResults(null);
    setMessage('');
    
    try {
      const result = await apiService.validateQuestionPaperJSON(subjectName, questionsData);
      setResults(result);
      setMessage('Validation completed successfully!');
      setMessageType('success');
    } catch (error) {
      setMessage(error.response?.data?.error || 'Validation failed');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score) => {
    if (score >= 80) return 'bg-green-50';
    if (score >= 60) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-secondary-900">
            Validate Question Paper for {subjectName}
          </h2>
        </div>
        <div className="card-body">
          {message && (
            <Alert
              type={messageType}
              message={message}
              onClose={() => setMessage('')}
              className="mb-4"
            />
          )}
          
          <form onSubmit={handleValidate} className="space-y-4">
            {/* Upload Mode Toggle */}
            <div className="flex space-x-4 mb-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="json"
                  checked={uploadMode === 'json'}
                  onChange={(e) => setUploadMode(e.target.value)}
                  className="mr-2"
                />
                Paste JSON Data
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="file"
                  checked={uploadMode === 'file'}
                  onChange={(e) => setUploadMode(e.target.value)}
                  className="mr-2"
                />
                Upload JSON File
              </label>
            </div>

            {uploadMode === 'json' ? (
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Question Paper JSON Data
                </label>
                <textarea
                  value={jsonData}
                  onChange={(e) => setJsonData(e.target.value)}
                  className="input-field"
                  rows="10"
                  placeholder={`[
  {
    "question": "Unit I - 1a",
    "text": "Define operating system and explain its functions"
  },
  {
    "question": "Unit I - 1b", 
    "text": "What are system calls? Explain with examples"
  }
]`}
                />
                <p className="text-xs text-secondary-500 mt-1">
                  Enter questions in JSON format as an array of objects with "question" and "text" fields
                </p>
              </div>
            ) : (
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
                    <div className="text-xs text-green-600">{(file.size / 1024).toFixed(2)} KB</div>
                    <button
                      type="button"
                      onClick={() => {setFile(null); setJsonData('');}}
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
                      <label htmlFor="question-paper-upload" className="cursor-pointer">
                        <span className="text-primary-600 font-medium hover:text-primary-500">
                          Click to upload
                        </span>
                        <span> or drag and drop</span>
                      </label>
                      <input
                        id="question-paper-upload"
                        name="question-paper-upload"
                        type="file"
                        accept=".json"
                        className="sr-only"
                        onChange={handleFileSelect}
                      />
                    </div>
                    <p className="text-xs text-secondary-500">JSON files only</p>
                  </div>
                )}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || (uploadMode === 'json' ? !jsonData.trim() : !file)}
              className="btn-primary flex items-center w-full justify-center"
            >
              {loading && <LoadingSpinner size="sm" className="mr-2" />}
              {loading ? 'Validating...' : 'Validate Question Paper'}
            </button>
          </form>
        </div>
      </div>

      {/* Results Section */}
      {results && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className={`card ${getScoreBg(results.average_score)}`}>
              <div className="card-body text-center">
                <div className={`text-2xl font-bold ${getScoreColor(results.average_score)}`}>
                  {Math.round(results.average_score)}%
                </div>
                <div className="text-sm text-secondary-700">Overall Score</div>
              </div>
            </div>
            
            <div className="card bg-blue-50">
              <div className="card-body text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {results.total_questions}
                </div>
                <div className="text-sm text-secondary-700">Questions Found</div>
              </div>
            </div>
            
            <div className="card bg-purple-50">
              <div className="card-body text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {results.subject_name}
                </div>
                <div className="text-sm text-secondary-700">Subject</div>
              </div>
            </div>
          </div>

          {/* Questions Analysis */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-secondary-900">Question Analysis</h3>
            </div>
            <div className="card-body">
              <div className="space-y-6">
                {results.validation_results?.map((result, index) => (
                  <div key={index} className="border border-secondary-200 rounded-lg p-4">
                    <div className="mb-3">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-medium text-secondary-900">{result.question_id}</h4>
                          <p className="text-sm text-secondary-600 mt-1">{result.question_text}</p>
                        </div>
                        <div className={`text-lg font-bold ${getScoreColor(result.overall_score)}`}>
                          {Math.round(result.overall_score)}%
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Syllabus Validation */}
                      {result.syllabus_validation && (
                        <div className="bg-gray-50 p-3 rounded">
                          <h5 className="font-medium text-gray-900 mb-2">Syllabus Coverage</h5>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-sm">Covered:</span>
                              <span className={`text-sm font-medium ${
                                result.syllabus_validation.is_covered ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {result.syllabus_validation.is_covered ? 'Yes' : 'No'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm">Score:</span>
                              <span className="text-sm font-medium">
                                {result.syllabus_validation.coverage_percentage}%
                              </span>
                            </div>
                            {result.syllabus_validation.reasoning && (
                              <p className="text-xs text-gray-600 mt-2">
                                {result.syllabus_validation.reasoning}
                              </p>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Textbook Validation */}
                      {result.textbook_validation && (
                        <div className="bg-blue-50 p-3 rounded">
                          <h5 className="font-medium text-blue-900 mb-2">Textbook Support</h5>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-sm">Supported:</span>
                              <span className={`text-sm font-medium ${
                                result.textbook_validation.is_supported ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {result.textbook_validation.is_supported ? 'Yes' : 'No'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm">Score:</span>
                              <span className="text-sm font-medium">
                                {result.textbook_validation.support_percentage}%
                              </span>
                            </div>
                            {result.textbook_validation.reasoning && (
                              <p className="text-xs text-blue-600 mt-2">
                                {result.textbook_validation.reasoning}
                              </p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Recommendations */}
                    {result.recommendations && result.recommendations.length > 0 && (
                      <div className="mt-3 p-3 bg-yellow-50 rounded">
                        <h5 className="font-medium text-yellow-900 mb-2">Recommendations</h5>
                        <ul className="text-sm text-yellow-800 space-y-1">
                          {result.recommendations.map((rec, idx) => (
                            <li key={idx} className="flex items-start">
                              <span className="mr-2">•</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuestionPaperValidator;
