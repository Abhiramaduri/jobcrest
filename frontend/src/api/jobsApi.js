import axiosInstance from './axiosInstance';

export const jobsApi = {
  getJobs: async (params = {}) => {
    // Clean empty parameters
    const cleanParams = {};
    Object.keys(params).forEach(key => {
      if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
        cleanParams[key] = params[key];
      }
    });
    const response = await axiosInstance.get('/jobs/', { params: cleanParams });
    return response.data;
  },

  getJobDetail: async (slug) => {
    const response = await axiosInstance.get(`/jobs/${slug}/`);
    return response.data;
  },

  createJob: async (jobData) => {
    const response = await axiosInstance.post('/jobs/', jobData);
    return response.data;
  },

  updateJob: async (slug, jobData) => {
    const response = await axiosInstance.patch(`/jobs/${slug}/`, jobData);
    return response.data;
  },

  deleteJob: async (slug) => {
    const response = await axiosInstance.delete(`/jobs/${slug}/`);
    return response.data;
  },

  updateJobStatus: async (slug, status) => {
    const response = await axiosInstance.patch(`/jobs/${slug}/status/`, { status });
    return response.data;
  },

  getMyPostings: async () => {
    const response = await axiosInstance.get('/jobs/my-postings/');
    return response.data;
  },

  getRecommendedJobs: async () => {
    const response = await axiosInstance.get('/jobs/recommended/');
    return response.data;
  },

  getSavedJobs: async () => {
    const response = await axiosInstance.get('/jobs/saved/');
    return response.data;
  },

  saveJob: async (slug) => {
    const response = await axiosInstance.post(`/jobs/${slug}/save/`);
    return response.data;
  },

  unsaveJob: async (slug) => {
    // Django backend supports POST or DELETE to /jobs/<slug>/unsave/
    try {
      const response = await axiosInstance.post(`/jobs/${slug}/unsave/`);
      return response.data;
    } catch {
      const response = await axiosInstance.delete(`/jobs/${slug}/unsave/`);
      return response.data;
    }
  },

  getCategories: async () => {
    const response = await axiosInstance.get('/jobs/categories/');
    return response.data;
  },

  getSkills: async () => {
    const response = await axiosInstance.get('/jobs/skills/');
    return response.data;
  },
};

export default jobsApi;
