import api from './api';

export const userService = {
  // Get available subjects
  getSubjects: async () => {
    const response = await api.get('/user/subjects');
    return response.data;
  },

  // Validate question paper
  validateQuestionPaper: async (subjectId, formData) => {
    const response = await api.post(`/user/subjects/${subjectId}/validate`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Preview question paper
  previewQuestionPaper: async (formData) => {
    const response = await api.post('/user/preview', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get validation history (if implemented in backend)
  getValidationHistory: async () => {
    const response = await api.get('/user/history');
    return response.data;
  }
};
