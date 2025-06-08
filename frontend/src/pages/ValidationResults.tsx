import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getValidationResult, getAllSyllabi, getAllQuestionPapers } from '../services/api';

interface Syllabus {
  _id: string;
  name: string;
  course_name: string;
}

interface QuestionPaper {
  _id: string;
  name: string;
}

interface ValidationItem {
  question_identifier: string;
  question_text: string;
  syllabus_status: string;
  syllabus_reasoning: string;
  textbook_coverage_status: string;
  textbook_reasoning: string;
}

interface ValidationResultData {
  _id: string;
  syllabus_id: string;
  question_paper_id: string;
  validation_summary: ValidationItem[];
  errors: string[];
  created_at: string;
}

const ValidationResults: React.FC = () => {
  const { resultId } = useParams<{ resultId: string }>();
  const [result, setResult] = useState<ValidationResultData | null>(null);
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [questionPapers, setQuestionPapers] = useState<QuestionPaper[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!resultId) return;
      
      try {
        setLoading(true);
        
        const [resultRes, syllabiRes, qpRes] = await Promise.all([
          getValidationResult(resultId),
          getAllSyllabi(),
          getAllQuestionPapers()
        ]);
        
        setResult(resultRes.data.result);
        setSyllabi(syllabiRes.data.syllabi || []);
        setQuestionPapers(qpRes.data.question_papers || []);
        
        setError(null);
      } catch (err: any) {
        console.error('Error fetching validation result:', err);
        setError(err.response?.data?.error || 'Failed to fetch validation result. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [resultId]);
  
  const findSyllabusName = (id: string): string => {
    const syllabus = syllabi.find(s => s._id === id);
    return syllabus ? `${syllabus.name} - ${syllabus.course_name}` : 'Unknown Syllabus';
  };
  
  const findQuestionPaperName = (id: string): string => {
    const questionPaper = questionPapers.find(qp => qp._id === id);
    return questionPaper ? questionPaper.name : 'Unknown Question Paper';
  };
  
  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600 mr-2"></div>
        <p className="text-lg">Loading validation result...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded my-4">
        <p className="font-bold">Error:</p>
        <p>{error}</p>
        <Link to="/" className="text-blue-600 hover:text-blue-800 mt-4 inline-block">
          Return to Dashboard
        </Link>
      </div>
    );
  }
  
  if (!result) {
    return (
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded my-4">
        <p>No validation result found with ID: {resultId}</p>
        <Link to="/" className="text-blue-600 hover:text-blue-800 mt-4 inline-block">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const inSyllabusCount = result.validation_summary.filter(item => item.syllabus_status === 'IN_SYLLABUS').length;
  const outOfSyllabusCount = result.validation_summary.filter(item => item.syllabus_status === 'OUT_OF_SYLLABUS').length;
  const inTextbookCount = result.validation_summary.filter(item => item.textbook_coverage_status === 'YES_IN_TEXTBOOK').length;
  const notInTextbookCount = result.validation_summary.filter(item => item.textbook_coverage_status === 'NO_IN_PROVIDED_TEXTBOOK_EXCERPTS').length;

  return (
    <div>
      <div className="mb-6">
        <Link to="/" className="text-blue-600 hover:text-blue-800">
          &larr; Back to Dashboard
        </Link>
      </div>
      
      <h1 className="text-3xl font-bold mb-4">Validation Results</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">Summary</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <p className="font-medium">Question Paper:</p>
            <p className="text-gray-700">{findQuestionPaperName(result.question_paper_id)}</p>
          </div>
          <div>
            <p className="font-medium">Syllabus:</p>
            <p className="text-gray-700">{findSyllabusName(result.syllabus_id)}</p>
          </div>
          <div>
            <p className="font-medium">Total Questions:</p>
            <p className="text-gray-700">{result.validation_summary.length}</p>
          </div>
          <div>
            <p className="font-medium">Validation Date:</p>
            <p className="text-gray-700">{new Date(result.created_at).toLocaleString()}</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-green-100 p-3 rounded-lg text-center">
            <p className="text-2xl font-bold text-green-700">{inSyllabusCount}</p>
            <p className="text-sm text-green-800">In Syllabus</p>
          </div>
          <div className="bg-red-100 p-3 rounded-lg text-center">
            <p className="text-2xl font-bold text-red-700">{outOfSyllabusCount}</p>
            <p className="text-sm text-red-800">Out of Syllabus</p>
          </div>
          <div className="bg-blue-100 p-3 rounded-lg text-center">
            <p className="text-2xl font-bold text-blue-700">{inTextbookCount}</p>
            <p className="text-sm text-blue-800">Covered in Textbook</p>
          </div>
          <div className="bg-yellow-100 p-3 rounded-lg text-center">
            <p className="text-2xl font-bold text-yellow-700">{notInTextbookCount}</p>
            <p className="text-sm text-yellow-800">Not in Textbook</p>
          </div>
        </div>
      </div>
      
      {result.errors && result.errors.length > 0 && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
          <div className="flex">
            <div>
              <p className="font-bold">Warnings/Errors:</p>
              <ul className="list-disc ml-5">
                {result.errors.map((error, idx) => (
                  <li key={idx} className="text-sm text-yellow-700">{error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Detailed Results</h2>
        
        <div className="divide-y">
          {result.validation_summary.map((item, idx) => (
            <div key={idx} className="py-4">
              <div className="flex flex-col md:flex-row md:justify-between md:items-start mb-2">
                <h3 className="text-lg font-medium">{item.question_identifier}</h3>
                <div className="flex space-x-2 mt-1 md:mt-0">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    item.syllabus_status === 'IN_SYLLABUS' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {item.syllabus_status}
                  </span>
                  {item.syllabus_status === 'IN_SYLLABUS' && (
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      item.textbook_coverage_status === 'YES_IN_TEXTBOOK'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {item.textbook_coverage_status === 'YES_IN_TEXTBOOK' ? 'IN TEXTBOOK' : 'NOT IN TEXTBOOK'}
                    </span>
                  )}
                </div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded mb-3">
                <p className="text-gray-800">{item.question_text}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-sm text-gray-700 mb-1">Syllabus Assessment:</h4>
                  <p className="text-sm bg-gray-50 p-2 rounded">{item.syllabus_reasoning}</p>
                </div>
                
                {item.syllabus_status === 'IN_SYLLABUS' && (
                  <div>
                    <h4 className="font-medium text-sm text-gray-700 mb-1">Textbook Assessment:</h4>
                    <p className="text-sm bg-gray-50 p-2 rounded">{item.textbook_reasoning}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ValidationResults;
