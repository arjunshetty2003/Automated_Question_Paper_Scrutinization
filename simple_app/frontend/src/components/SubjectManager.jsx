import React, { useState } from 'react';
import { apiService } from '../services/api';
import Alert from './Alert';
import LoadingSpinner from './LoadingSpinner';

const SubjectManager = ({ onSubjectCreated }) => {
  const [subjectName, setSubjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subjectName.trim()) return;

    setLoading(true);
    try {
      await apiService.createSubject(subjectName.trim());
      setMessage(`Subject "${subjectName}" created successfully!`);
      setMessageType('success');
      setSubjectName('');
      if (onSubjectCreated) onSubjectCreated();
    } catch (error) {
      setMessage(error.response?.data?.error || 'Failed to create subject');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-xl font-semibold text-secondary-900">Create New Subject</h2>
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
          <div>
            <label htmlFor="subjectName" className="block text-sm font-medium text-secondary-700 mb-2">
              Subject Name
            </label>
            <input
              type="text"
              id="subjectName"
              value={subjectName}
              onChange={(e) => setSubjectName(e.target.value)}
              className="input-field"
              placeholder="e.g., Operating Systems"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading || !subjectName.trim()}
            className="btn-primary flex items-center"
          >
            {loading && <LoadingSpinner size="sm" className="mr-2" />}
            Create Subject
          </button>
        </form>
      </div>
    </div>
  );
};

export default SubjectManager;
