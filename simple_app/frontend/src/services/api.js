import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Get all subjects
  getSubjects: async () => {
    const response = await api.get('/subjects');
    return response.data;
  },

  // Create a new subject
  createSubject: async (name) => {
    const response = await api.post('/subjects', { subject_name: name });
    return response.data;
  },

  // Upload syllabus for a subject
  uploadSyllabus: async (subjectName, syllabusData) => {
    const response = await api.post(`/subjects/${subjectName}/syllabus`, syllabusData);
    return response.data;
  },

  // Upload textbooks for a subject
  uploadTextbooks: async (subjectName, files) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    const response = await api.post(`/subjects/${subjectName}/textbooks`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Validate question paper
  validateQuestionPaper: async (subjectName, file) => {
    const formData = new FormData();
    formData.append('question_paper', file);
    
    const response = await api.post(`/validate/${subjectName}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Validate question paper with JSON data
  validateQuestionPaperJSON: async (subjectName, questionsData) => {
    const response = await api.post(`/validate-json/${subjectName}`, {
      questions: questionsData
    });
    return response.data;
  },
};
