import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadQuestionPaper, getAllSyllabi, getAllTextbooks, validateQuestionPaper } from '../services/api';

interface Syllabus {
  _id: string;
  name: string;
  course_name: string;
}

interface Textbook {
  _id: string;
  name: string;
  syllabus_id: string;
}

const QuestionPaperUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [textbooks, setTextbooks] = useState<Textbook[]>([]);
  const [selectedSyllabus, setSelectedSyllabus] = useState<string>('');
  const [selectedTextbooks, setSelectedTextbooks] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [resultId, setResultId] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [syllabiRes, textbooksRes] = await Promise.all([
          getAllSyllabi(),
          getAllTextbooks()
        ]);
        
        setSyllabi(syllabiRes.data.syllabi || []);
        setTextbooks(textbooksRes.data.textbooks || []);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch syllabi and textbooks. Please try again later.');
      }
    };

    fetchData();
  }, []);

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

  const handleSyllabusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const syllabus = e.target.value;
    setSelectedSyllabus(syllabus);
    // Reset textbook selection when syllabus changes
    setSelectedTextbooks([]);
  };

  const handleTextbookChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const options = e.target.options;
    const values: string[] = [];
    for (let i = 0; i < options.length; i++) {
      if (options[i].selected) {
        values.push(options[i].value);
      }
    }
    setSelectedTextbooks(values);
  };

  const filteredTextbooks = textbooks.filter(textbook => 
    textbook.syllabus_id === selectedSyllabus
  );

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
      
      // First upload the question paper
      const uploadResponse = await uploadQuestionPaper(formData);
      const questionPaperId = uploadResponse.data.question_paper_id;
      
      setSuccess('Question paper uploaded successfully! Starting validation...');
      
      // Then validate it
      const validationResponse = await validateQuestionPaper({
        question_paper_id: questionPaperId,
        syllabus_id: selectedSyllabus,
        textbook_ids: selectedTextbooks
      });
      
      setResultId(validationResponse.data.result_id);
      setSuccess('Validation completed successfully!');
      
      // Redirect to results page after 2 seconds
      setTimeout(() => {
        navigate(`/results/${validationResponse.data.result_id}`);
      }, 2000);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.response?.data?.error || 'Failed to process question paper. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Upload Question Paper</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-md max-w-xl mx-auto">
        <div className="mb-4">
          <p className="text-gray-700 mb-2">
            Upload a question paper JSON file to validate against a syllabus and textbooks.
          </p>
          <p className="text-sm text-gray-500 mb-4">
            The JSON file should contain an array of questions with 'question' identifier and 'text' fields.
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
            {resultId && (
              <p className="mt-2">
                You will be redirected to the results page shortly...
              </p>
            )}
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
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="textbook-select">
              Select Textbooks (optional, hold Ctrl/Cmd to select multiple)
            </label>
            <select
              id="textbook-select"
              multiple
              value={selectedTextbooks}
              onChange={handleTextbookChange}
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32"
              disabled={loading || !selectedSyllabus || filteredTextbooks.length === 0}
            >
              {filteredTextbooks.map((textbook) => (
                <option key={textbook._id} value={textbook._id}>
                  {textbook.name}
                </option>
              ))}
            </select>
            {selectedSyllabus && filteredTextbooks.length === 0 && (
              <p className="mt-2 text-sm text-amber-600">
                No textbooks available for this syllabus. You can still validate against the syllabus only.
              </p>
            )}
          </div>
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="question-paper-file">
              Question Paper JSON File
            </label>
            <input
              type="file"
              id="question-paper-file"
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
              disabled={loading || !file || !selectedSyllabus}
            >
              {loading ? 'Processing...' : 'Upload & Validate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QuestionPaperUpload;
