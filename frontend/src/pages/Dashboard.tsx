import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAllSyllabi, getAllTextbooks, getAllQuestionPapers, getAllResults } from '../services/api';

interface Syllabus {
  _id: string;
  name: string;
  course_name: string;
  vectorized: boolean;
  created_at: string;
}

interface Textbook {
  _id: string;
  name: string;
  syllabus_id: string;
  vectorized: boolean;
  created_at: string;
}

interface QuestionPaper {
  _id: string;
  name: string;
  syllabus_id: string;
  created_at: string;
}

interface ValidationResult {
  _id: string;
  syllabus_id: string;
  question_paper_id: string;
  textbook_ids: string[];
  created_at: string;
}

const Dashboard: React.FC = () => {
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [textbooks, setTextbooks] = useState<Textbook[]>([]);
  const [questionPapers, setQuestionPapers] = useState<QuestionPaper[]>([]);
  const [results, setResults] = useState<ValidationResult[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [syllabiRes, textbooksRes, questionPapersRes, resultsRes] = await Promise.all([
          getAllSyllabi(),
          getAllTextbooks(),
          getAllQuestionPapers(),
          getAllResults()
        ]);
        
        setSyllabi(syllabiRes.data.syllabi || []);
        setTextbooks(textbooksRes.data.textbooks || []);
        setQuestionPapers(questionPapersRes.data.question_papers || []);
        setResults(resultsRes.data.results || []);
        
        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const findSyllabusName = (id: string): string => {
    const syllabus = syllabi.find(s => s._id === id);
    return syllabus ? syllabus.name : 'Unknown Syllabus';
  };
  
  const findQuestionPaperName = (id: string): string => {
    const questionPaper = questionPapers.find(qp => qp._id === id);
    return questionPaper ? questionPaper.name : 'Unknown Question Paper';
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      {loading ? (
        <div className="text-center">
          <p className="text-lg">Loading data...</p>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 flex items-center justify-between">
              Syllabi
              <Link to="/upload-syllabus" className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                + Add New
              </Link>
            </h2>
            {syllabi.length === 0 ? (
              <p className="text-gray-500">No syllabi uploaded yet.</p>
            ) : (
              <ul className="divide-y">
                {syllabi.map(syllabus => (
                  <li key={syllabus._id} className="py-3">
                    <div className="flex flex-col">
                      <span className="font-medium">{syllabus.name}</span>
                      <span className="text-sm text-gray-600">Course: {syllabus.course_name}</span>
                      <span className="text-sm text-gray-600">
                        Uploaded: {new Date(syllabus.created_at).toLocaleDateString()}
                      </span>
                      <span className={`text-xs mt-1 ${syllabus.vectorized ? 'text-green-600' : 'text-red-600'}`}>
                        {syllabus.vectorized ? 'Processed ✓' : 'Processing...'}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 flex items-center justify-between">
              Textbooks
              <Link to="/upload-textbook" className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                + Add New
              </Link>
            </h2>
            {textbooks.length === 0 ? (
              <p className="text-gray-500">No textbooks uploaded yet.</p>
            ) : (
              <ul className="divide-y">
                {textbooks.map(textbook => (
                  <li key={textbook._id} className="py-3">
                    <div className="flex flex-col">
                      <span className="font-medium">{textbook.name}</span>
                      <span className="text-sm text-gray-600">
                        Related to: {findSyllabusName(textbook.syllabus_id)}
                      </span>
                      <span className="text-sm text-gray-600">
                        Uploaded: {new Date(textbook.created_at).toLocaleDateString()}
                      </span>
                      <span className={`text-xs mt-1 ${textbook.vectorized ? 'text-green-600' : 'text-red-600'}`}>
                        {textbook.vectorized ? 'Processed ✓' : 'Processing...'}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 flex items-center justify-between">
              Question Papers
              <Link to="/upload-question-paper" className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                + Add New
              </Link>
            </h2>
            {questionPapers.length === 0 ? (
              <p className="text-gray-500">No question papers uploaded yet.</p>
            ) : (
              <ul className="divide-y">
                {questionPapers.map(questionPaper => (
                  <li key={questionPaper._id} className="py-3">
                    <div className="flex flex-col">
                      <span className="font-medium">{questionPaper.name}</span>
                      <span className="text-sm text-gray-600">
                        Related to: {findSyllabusName(questionPaper.syllabus_id)}
                      </span>
                      <span className="text-sm text-gray-600">
                        Uploaded: {new Date(questionPaper.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Recent Validation Results</h2>
            {results.length === 0 ? (
              <p className="text-gray-500">No validations performed yet.</p>
            ) : (
              <ul className="divide-y">
                {results.slice(0, 5).map(result => (
                  <li key={result._id} className="py-3">
                    <div className="flex flex-col">
                      <Link to={`/results/${result._id}`} className="font-medium text-blue-600 hover:underline">
                        {findQuestionPaperName(result.question_paper_id)}
                      </Link>
                      <span className="text-sm text-gray-600">
                        Syllabus: {findSyllabusName(result.syllabus_id)}
                      </span>
                      <span className="text-sm text-gray-600">
                        Validated: {new Date(result.created_at).toLocaleDateString()}
                      </span>
                      <span className="text-xs text-gray-600 mt-1">
                        With {result.textbook_ids.length} textbook{result.textbook_ids.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 