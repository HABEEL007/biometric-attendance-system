import axios from 'axios';

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to attach token
apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle 401s
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Exclude /auth/login from redirecting to prevent page refresh loop on bad passwords
    const isLoginEndpoint = error.config && error.config.url && error.config.url.includes('/auth/login');
    
    if (error.response && error.response.status === 401 && !isLoginEndpoint) {
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const getStaff = async () => {
  const response = await apiClient.get('/staff');
  return response.data;
};

export const deleteStaff = async (employeeId) => {
  const response = await apiClient.delete(`/staff/${employeeId}`);
  return response.data;
};

export const enrollStaff = async (payload) => {
  const response = await apiClient.post('/enrollment/enroll', payload);
  return response.data;
};

export const getAuditLogs = async () => {
  const response = await apiClient.get('/attendance/today');
  return response.data;
};

export const getAttendanceReport = async (date) => {
  const response = await apiClient.get(`/attendance/report?date=${date}`);
  return response.data;
};

export const deleteAttendanceRecord = async (recordId) => {
  const response = await apiClient.delete(`/attendance/records/${recordId}`);
  return response.data;
};

export const startCamera = async (payload) => {
  const response = await apiClient.post('/camera/start', payload);
  return response.data;
};

export const stopCamera = async () => {
  const response = await apiClient.post('/camera/stop');
  return response.data;
};

export const startWebRTC = async (offer) => {
  const response = await apiClient.post('/camera/webrtc/offer', offer);
  return response.data;
};

export const getCameraStatus = async () => {
  const response = await apiClient.get('/camera/status');
  return response.data;
};

export const processSnapshot = async () => {
  const response = await apiClient.get('/camera/snapshot');
  return response.data;
};

export const verifyFrame = async (payload) => {
  const response = await apiClient.post('/attendance/verify-frame', payload);
  return response.data;
};

export const login = async (payload) => {
  const response = await apiClient.post('/auth/login', payload);
  return response.data;
};

export const signup = async (payload) => {
  const response = await apiClient.post('/auth/signup', payload);
  return response.data;
};

export const getSettings = async () => {
  const response = await apiClient.get('/settings');
  return response.data;
};

export const updateSettings = async (payload) => {
  const response = await apiClient.post('/settings', payload);
  return response.data;
};

// You can add more API calls here as needed
export default apiClient;
