import axios from 'axios';

// Direct connection to backend for debugging
const API_URL = 'http://localhost:5666/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Syllabus API
export const uploadSyllabus = (formData: FormData) => {
  return api.post('/syllabus', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getAllSyllabi = () => {
  return api.get('/syllabus/all');
};

// Textbook API
export const uploadTextbook = (formData: FormData) => {
  return api.post('/textbook', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getAllTextbooks = () => {
  return api.get('/textbooks/all');
};

// Question Paper API
export const uploadQuestionPaper = (formData: FormData) => {
  return api.post('/question-paper', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getAllQuestionPapers = () => {
  return api.get('/question-papers/all');
};

// Validation API
export const validateQuestionPaper = (data: {
  question_paper_id: string;
  syllabus_id: string;
  textbook_ids: string[];
}) => {
  return api.post('/validate', data);
};

export const getValidationResult = (resultId: string) => {
  return api.get(`/results/${resultId}`);
};

export const getAllResults = () => {
  return api.get('/results/all');
}; 