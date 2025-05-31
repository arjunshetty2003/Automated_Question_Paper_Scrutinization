import api from './api';

export const adminService = {
  // Subject management
  createSubject: async (subjectData) => {
    const response = await api.post('/admin/subjects', subjectData);
    return response.data;
  },

  updateSubject: async (subjectId, subjectData) => {
    const response = await api.put(`/admin/subjects/${subjectId}`, subjectData);
    return response.data;
  },

  deleteSubject: async (subjectId) => {
    const response = await api.delete(`/admin/subjects/${subjectId}`);
    return response.data;
  },

  getSubjects: async () => {
    const response = await api.get('/admin/subjects');
    return response.data;
  },

  // Syllabus management
  uploadSyllabus: async (subjectId, formData) => {
    const response = await api.post(`/admin/subjects/${subjectId}/syllabus`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Textbook management
  uploadTextbook: async (subjectId, formData) => {
    const response = await api.post(`/admin/subjects/${subjectId}/textbooks`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Generate embeddings
  generateEmbeddings: async (subjectId) => {
    const response = await api.post(`/admin/subjects/${subjectId}/generate-embeddings`);
    return response.data;
  },

  // Get subject details
  getSubjectDetails: async (subjectId) => {
    const response = await api.get(`/admin/subjects/${subjectId}`);
    return response.data;
  }
};
