import axios from 'axios';

const API_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStaff = async () => {
  const response = await apiClient.get('/staff');
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

// You can add more API calls here as needed
export default apiClient;
