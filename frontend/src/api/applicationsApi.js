import axiosInstance from './axiosInstance';

export const applicationsApi = {
  applyToJob: async (data) => {
    // Check if data is FormData (file upload) or plain JSON
    const isFormData = data instanceof FormData;
    const config = isFormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : {};
    const response = await axiosInstance.post('/applications/', data, config);
    return response.data;
  },

  getMyApplications: async () => {
    const response = await axiosInstance.get('/applications/my-applications/');
    return response.data;
  },

  withdrawApplication: async (id) => {
    const response = await axiosInstance.delete(`/applications/${id}/`);
    return response.data;
  },

  getApplicationsByJob: async (jobId) => {
    const response = await axiosInstance.get(`/applications/job/${jobId}/`);
    return response.data;
  },

  getApplicationDetail: async (id) => {
    const response = await axiosInstance.get(`/applications/${id}/`);
    return response.data;
  },

  updateApplicationStatus: async (id, status, notes = '') => {
    const response = await axiosInstance.patch(`/applications/${id}/status/`, {
      status,
      notes,
    });
    return response.data;
  },

  getApplicationHistory: async (id) => {
    const response = await axiosInstance.get(`/applications/${id}/history/`);
    return response.data;
  },

  scheduleInterview: async (interviewData) => {
    const response = await axiosInstance.post('/interviews/', interviewData);
    return response.data;
  },

  getMyInterviews: async () => {
    const response = await axiosInstance.get('/interviews/my-interviews/');
    return response.data;
  },

  getEmployerInterviews: async () => {
    const response = await axiosInstance.get('/interviews/employer/');
    return response.data;
  },

  updateInterview: async (id, interviewData) => {
    const response = await axiosInstance.patch(`/interviews/${id}/`, interviewData);
    return response.data;
  },
};

export default applicationsApi;
