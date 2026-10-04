import apiClient from './client';

export async function getLabResults() {
  const response = await apiClient.get('/api/lab-results/');
  return response.data;
}

export async function getLabResultsByDate(date) {
  const response = await apiClient.get(`/api/lab-results/date/${date}`);
  return response.data;
}

export async function createLabResult(data) {
  const response = await apiClient.post('/api/lab-results/', data);
  return response.data;
}

export async function updateLabResult(id, data) {
  const response = await apiClient.put(`/api/lab-results/${id}`, data);
  return response.data;
}

export async function deleteLabResult(id) {
  const response = await apiClient.delete(`/api/lab-results/${id}`);
  return response.data;
}
