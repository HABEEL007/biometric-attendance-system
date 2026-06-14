import axios from 'axios';

const API_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to attach token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle 401s
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
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

export const startCamera = async (payload) => {
  const response = await apiClient.post('/camera/start', payload);
  return response.data;
};

export const stopCamera = async () => {
  const response = await apiClient.post('/camera/stop');
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

// You can add more API calls here as needed
export default apiClient;
