import axiosInstance from './axiosInstance';

export const companyApi = {
  getCompanies: async () => {
    const response = await axiosInstance.get('/companies/');
    return response.data;
  },

  getCompany: async (slug) => {
    const response = await axiosInstance.get(`/companies/${slug}/`);
    return response.data;
  },

  createCompany: async (companyData) => {
    const isFormData = companyData instanceof FormData;
    const config = isFormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : {};
    const response = await axiosInstance.post('/companies/', companyData, config);
    return response.data;
  },

  updateCompany: async (slug, companyData) => {
    const isFormData = companyData instanceof FormData;
    const config = isFormData ? { headers: { 'Content-Type': 'multipart/form-data' } } : {};
    const response = await axiosInstance.patch(`/companies/${slug}/`, companyData, config);
    return response.data;
  },

  getCompanyRecruiters: async (slug) => {
    const response = await axiosInstance.get(`/companies/${slug}/recruiters/`);
    return response.data;
  },

  addRecruiter: async (slug, recruiterData) => {
    const response = await axiosInstance.post(`/companies/${slug}/recruiters/`, recruiterData);
    return response.data;
  },

  getEmployerProfile: async () => {
    // Check either /employer/profile/ or /employers/profile/
    const response = await axiosInstance.get('/employers/profile/');
    return response.data;
  },

  updateEmployerProfile: async (profileData) => {
    const response = await axiosInstance.patch('/employers/profile/', profileData);
    return response.data;
  },
};

export default companyApi;
