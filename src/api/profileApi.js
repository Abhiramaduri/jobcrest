import axiosInstance from './axiosInstance';

export const profileApi = {
  getProfile: async () => {
    const response = await axiosInstance.get('/jobseeker/profile/');
    return response.data;
  },

  updateProfile: async (data) => {
    const isFormData = data instanceof FormData;
    const config = isFormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : {};
    const response = await axiosInstance.patch('/jobseeker/profile/', data, config);
    return response.data;
  },

  uploadResume: async (file) => {
    const formData = new FormData();
    formData.append('resume', file);
    const response = await axiosInstance.post('/jobseeker/profile/resume/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getPublicProfile: async (id) => {
    const response = await axiosInstance.get(`/jobseeker/profile/${id}`);
    return response.data;
  },

  // Education
  getEducation: async () => {
    const response = await axiosInstance.get('/jobseeker/education/');
    return response.data;
  },

  addEducation: async (eduData) => {
    const response = await axiosInstance.post('/jobseeker/education/', eduData);
    return response.data;
  },

  updateEducation: async (id, eduData) => {
    const response = await axiosInstance.patch(`/jobseeker/education/${id}/`, eduData);
    return response.data;
  },

  deleteEducation: async (id) => {
    const response = await axiosInstance.delete(`/jobseeker/education/${id}/`);
    return response.data;
  },

  // Experience
  getExperience: async () => {
    const response = await axiosInstance.get('/jobseeker/experience/');
    return response.data;
  },

  addExperience: async (expData) => {
    const response = await axiosInstance.post('/jobseeker/experience/', expData);
    return response.data;
  },

  updateExperience: async (id, expData) => {
    const response = await axiosInstance.patch(`/jobseeker/experience/${id}/`, expData);
    return response.data;
  },

  deleteExperience: async (id) => {
    const response = await axiosInstance.delete(`/jobseeker/experience/${id}/`);
    return response.data;
  },

  // Skills
  getSkills: async () => {
    const response = await axiosInstance.get('/jobseeker/skills/');
    return response.data;
  },

  addSkill: async (skillData) => {
    const response = await axiosInstance.post('/jobseeker/skills/', skillData);
    return response.data;
  },

  deleteSkill: async (id) => {
    const response = await axiosInstance.delete(`/jobseeker/skills/${id}/`);
    return response.data;
  },

  getAllSkillsRepo: async () => {
    const response = await axiosInstance.get('/skills/');
    return response.data;
  },
};

export default profileApi;
