import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadTextbook, getAllSyllabi } from '../services/api';

interface Syllabus {
  _id: string;
  name: string;
  course_name: string;
}

const TextbookUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [selectedSyllabus, setSelectedSyllabus] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSyllabi = async () => {
      try {
        const response = await getAllSyllabi();
        setSyllabi(response.data.syllabi || []);
      } catch (err) {
        console.error('Error fetching syllabi:', err);
        setError('Failed to fetch syllabi. Please try again later.');
      }
    };

    fetchSyllabi();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        setError('Please select a PDF file');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleSyllabusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedSyllabus(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!selectedSyllabus) {
      setError('Please select a syllabus');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('syllabus_id', selectedSyllabus);
      
      const response = await uploadTextbook(formData);
      
      setSuccess(`Textbook uploaded successfully!`);
      setFile(null);
      
      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err: any) {
      console.error('Error uploading textbook:', err);
      setError(err.response?.data?.error || 'Failed to upload textbook. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Upload Textbook</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-md max-w-xl mx-auto">
        <div className="mb-4">
          <p className="text-gray-700 mb-2">
            Upload a textbook PDF file to be used for validating question papers.
          </p>
          <p className="text-sm text-gray-500 mb-4">
            The textbook should be associated with a syllabus.
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
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="syllabus-select">
              Select Syllabus
            </label>
            <select
              id="syllabus-select"
              value={selectedSyllabus}
              onChange={handleSyllabusChange}
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              disabled={loading || syllabi.length === 0}
            >
              <option value="">-- Select a Syllabus --</option>
              {syllabi.map((syllabus) => (
                <option key={syllabus._id} value={syllabus._id}>
                  {syllabus.name} - {syllabus.course_name}
                </option>
              ))}
            </select>
            {syllabi.length === 0 && (
              <p className="mt-2 text-sm text-red-500">
                No syllabi available. Please upload a syllabus first.
              </p>
            )}
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="textbook-file">
              Textbook PDF File
            </label>
            <input
              type="file"
              id="textbook-file"
              accept=".pdf"
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
                Selected file: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
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
              disabled={loading || !file || !selectedSyllabus}
            >
              {loading ? 'Uploading...' : 'Upload Textbook'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TextbookUpload;
