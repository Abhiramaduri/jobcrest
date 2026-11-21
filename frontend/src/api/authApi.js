import axiosInstance from './axiosInstance';

export const authApi = {
  // ── Registration OTP ──
  sendRegistrationOtp: async (email) => {
    const response = await axiosInstance.post('/auth/register/send-otp/', { email });
    return response.data;
  },

  register: async (payload) => {
    const role = payload.role === 'job_seeker' || payload.role === 'jobseeker' ? 'jobseeker' : 'employer';
    const body = {
      username: payload.username,
      email: payload.email,
      password: payload.password,
      password2: payload.passwordConfirm || payload.password,
      user_type: role,
      phone_number: payload.phone_number || payload.phone || '',
      otp: payload.otp || '',
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
    const response = await axiosInstance.post('/auth/logout/', { refresh: refreshToken });
    return response.data;
  },

  getMe: async () => {
    const response = await axiosInstance.get('/auth/me');
    return response.data;
  },

  // ── Forgot Password ──
  passwordReset: async (email) => {
    const response = await axiosInstance.post('/auth/password-reset/', { email });
    return response.data;
  },

  passwordResetVerifyOtp: async ({ email, otp }) => {
    const response = await axiosInstance.post('/auth/password-reset/verify-otp/', { email, otp });
    return response.data;
  },

  passwordResetConfirm: async ({ email, otp, new_password, confirm_password }) => {
    const response = await axiosInstance.post('/auth/password-reset-confirm/', {
      email, otp, new_password, confirm_password,
    });
    return response.data;
  },
};

export default authApi;
