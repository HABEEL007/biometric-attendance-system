import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const attendanceApi = {
  getToday: () => apiClient.get('/attendance/today'),
  getReport: (date) => apiClient.get(`/attendance/report?date=${date}`),
  manualCheckin: (data) => apiClient.post('/attendance/manual-checkin', data),
  verifyFrame: (data) => apiClient.post('/attendance/verify-frame', data),
};

export const staffApi = {
  list: () => apiClient.get('/staff'),
  get: (employeeId) => apiClient.get(`/staff/${employeeId}`),
  create: (data) => apiClient.post('/staff', data),
  delete: (employeeId) => apiClient.delete(`/staff/${employeeId}`),
};

export const enrollmentApi = {
  enroll: (data) => apiClient.post('/enrollment/enroll', data),
  checkStatus: (employeeId) => apiClient.get(`/enrollment/status/${employeeId}`),
};
