import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadSyllabus } from '../services/api';

const SyllabusUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/json') {
        setError('Please select a JSON file');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await uploadSyllabus(formData);
      
      setSuccess(`Syllabus uploaded successfully! Course: ${response.data.course_name}`);
      setFile(null);
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err: any) {
      console.error('Error uploading syllabus:', err);
      setError(err.response?.data?.error || 'Failed to upload syllabus. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Upload Syllabus</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-md max-w-xl mx-auto">
        <div className="mb-4">
          <p className="text-gray-700 mb-2">
            Upload a syllabus JSON file to process and validate against.
          </p>
          <p className="text-sm text-gray-500 mb-4">
            The JSON file should contain the course name, units, and syllabus content.
          </p>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <p>{error}</p>
          </div>
        )}
        
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            <p>{success}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="syllabus-file">
              Syllabus JSON File
            </label>
            <input
              type="file"
              id="syllabus-file"
              accept=".json"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500
                         file:mr-4 file:py-2 file:px-4
                         file:rounded-full file:border-0
                         file:text-sm file:font-semibold
                         file:bg-blue-50 file:text-blue-700
                         hover:file:bg-blue-100"
              disabled={loading}
            />
            {file && (
              <p className="mt-2 text-sm text-gray-500">
                Selected file: {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </p>
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              disabled={loading || !file}
            >
              {loading ? 'Uploading...' : 'Upload Syllabus'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SyllabusUpload; 