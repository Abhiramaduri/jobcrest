import axiosInstance from './axiosInstance';

export const authApi = {
  register: async (payload) => {
    // Normalizes user_type to 'jobseeker' or 'employer'
    const role = payload.role === 'job_seeker' || payload.role === 'jobseeker' ? 'jobseeker' : 'employer';
    const body = {
      username: payload.username,
      email: payload.email,
      password: payload.password,
      password2: payload.passwordConfirm || payload.password,
      user_type: role,
      phone_number: payload.phone_number || payload.phone || '',
    };
    const response = await axiosInstance.post('/auth/register/', body);
    return response.data;
  },

  login: async (credentials) => {
    const response = await axiosInstance.post('/auth/login/', {
      username: credentials.username || credentials.email,
      password: credentials.password,
    });
    return response.data;
  },

  logout: async (refreshToken) => {
    if (!refreshToken) return null;
    const response = await axiosInstance.post('/auth/logout/', {
      refresh: refreshToken,
    });
    return response.data;
  },

  getMe: async () => {
    const response = await axiosInstance.get('/auth/me');
    return response.data;
  },

  passwordReset: async (email) => {
    const response = await axiosInstance.post('/auth/password-reset/', { email });
    return response.data;
  },

  passwordResetConfirm: async (payload) => {
    const response = await axiosInstance.post('/auth/password-reset-confirm/', payload);
    return response.data;
  },
};

export default authApi;
