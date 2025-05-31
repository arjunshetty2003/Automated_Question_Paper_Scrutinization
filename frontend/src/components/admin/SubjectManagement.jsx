import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import LoadingSpinner from '../common/LoadingSpinner';
import Alert from '../common/Alert';

const SubjectManagement = () => {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: ''
  });

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const data = await adminService.getSubjects();
      setSubjects(data.subjects || []);
    } catch (error) {
      setError('Failed to fetch subjects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSubject = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await adminService.createSubject(formData);
      setSuccess('Subject created successfully!');
      setFormData({ name: '', code: '', description: '' });
      setShowCreateForm(false);
      fetchSubjects();
    } catch (error) {
      setError(error.response?.data?.message || 'Failed to create subject');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSubject = async (subjectId) => {
    if (!window.confirm('Are you sure you want to delete this subject?')) {
      return;
    }

    try {
      await adminService.deleteSubject(subjectId);
      setSuccess('Subject deleted successfully!');
      fetchSubjects();
    } catch (error) {
      setError(error.response?.data?.message || 'Failed to delete subject');
    }
  };

  if (loading && subjects.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-secondary-900">Subject Management</h1>
            <p className="mt-2 text-secondary-600">
              Create and manage subjects for question paper validation
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary"
          >
            Add New Subject
          </button>
        </div>
      </div>

      {error && (
        <Alert
          type="error"
          message={error}
          onClose={() => setError('')}
          className="mb-6"
        />
      )}

      {success && (
        <Alert
          type="success"
          message={success}
          onClose={() => setSuccess('')}
          className="mb-6"
        />
      )}

      {/* Create Subject Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">Create New Subject</h2>
            <form onSubmit={handleCreateSubject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Subject Name
                </label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Mathematics"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Subject Code
                </label>
                <input
                  type="text"
                  required
                  className="input-field"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  placeholder="e.g., MATH101"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Description
                </label>
                <textarea
                  className="input-field"
                  rows="3"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief description of the subject"
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary flex-1"
                >
                  {loading ? 'Creating...' : 'Create Subject'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Subjects List */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-secondary-900">All Subjects</h2>
        </div>
        <div className="card-body">
          {subjects.length === 0 ? (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-secondary-900">No subjects</h3>
              <p className="mt-1 text-sm text-secondary-500">Get started by creating a new subject.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {subjects.map((subject) => (
                <div key={subject._id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-secondary-900">{subject.name}</h3>
                      <p className="text-sm text-secondary-600">{subject.code}</p>
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
                  
                  <p className="text-sm text-secondary-700 mb-4">{subject.description}</p>
                  
                  <div className="space-y-2 mb-4 text-xs">
                    <div className="flex items-center">
                      <span className={`w-2 h-2 rounded-full mr-2 ${subject.syllabusUploaded ? 'bg-green-400' : 'bg-red-400'}`}></span>
                      <span className="text-secondary-600">
                        Syllabus {subject.syllabusUploaded ? 'Uploaded' : 'Not Uploaded'}
                      </span>
                    </div>
                    <div className="flex items-center">
                      <span className={`w-2 h-2 rounded-full mr-2 ${subject.textbooksCount > 0 ? 'bg-green-400' : 'bg-red-400'}`}></span>
                      <span className="text-secondary-600">
                        {subject.textbooksCount || 0} Textbook(s)
                      </span>
                    </div>
                    <div className="flex items-center">
                      <span className={`w-2 h-2 rounded-full mr-2 ${subject.embeddingsGenerated ? 'bg-green-400' : 'bg-red-400'}`}></span>
                      <span className="text-secondary-600">
                        Embeddings {subject.embeddingsGenerated ? 'Generated' : 'Not Generated'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => window.location.href = `/admin/subjects/${subject._id}`}
                      className="btn-primary text-xs flex-1"
                    >
                      Manage
                    </button>
                    <button
                      onClick={() => handleDeleteSubject(subject._id)}
                      className="btn-danger text-xs px-3"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SubjectManagement;
