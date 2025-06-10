import React, { useState } from 'react';
import { apiService } from '../services/api';
import Alert from './Alert';
import LoadingSpinner from './LoadingSpinner';

const TextbookUploader = ({ subjectName }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files).filter(file => 
      file.type === 'application/pdf'
    );
    setFiles(prev => [...prev, ...selectedFiles]);
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
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(file => 
      file.type === 'application/pdf'
    );
    setFiles(prev => [...prev, ...droppedFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setMessage('Please select at least one PDF file');
      setMessageType('error');
      return;
    }

    setLoading(true);
    try {
      const result = await apiService.uploadTextbooks(subjectName, files);
      setMessage(`${result.uploaded_files?.length || 0} textbook(s) uploaded successfully! Created ${result.documents_created} document chunks.`);
      setMessageType('success');
      setFiles([]);
    } catch (error) {
      setMessage(error.response?.data?.error || 'Failed to upload textbooks');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-xl font-semibold text-secondary-900">Upload Textbooks for {subjectName}</h2>
        <p className="text-sm text-secondary-600 mt-1">Upload PDF textbook files for analysis</p>
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
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              dragActive
                ? 'border-primary-400 bg-primary-50'
                : 'border-secondary-300 hover:border-secondary-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
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
                  multiple
                  accept=".pdf"
                  className="sr-only"
                  onChange={handleFileSelect}
                />
              </div>
              <p className="text-xs text-secondary-500">PDF files only, up to 16MB each</p>
            </div>
          </div>

          {files.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium text-secondary-900">Selected Files:</h4>
              {files.map((file, index) => (
                <div key={index} className="flex items-center justify-between bg-secondary-50 p-3 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <svg className="h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <p className="text-sm font-medium text-secondary-900">{file.name}</p>
                      <p className="text-xs text-secondary-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || files.length === 0}
            className="btn-primary w-full flex items-center justify-center"
          >
            {loading ? <LoadingSpinner size="sm" className="mr-2" /> : null}
            Upload Textbooks
          </button>
        </form>
        
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="text-sm font-medium text-blue-900 mb-2">📄 PDF Guidelines:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Upload textbook PDF files for automatic text extraction</li>
            <li>• Ensure PDFs contain selectable text (not scanned images)</li>
            <li>• Multiple files can be uploaded at once</li>
            <li>• Content will be automatically chunked for efficient search</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TextbookUploader;
