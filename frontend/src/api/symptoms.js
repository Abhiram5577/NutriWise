import apiClient from './client';

export async function getSymptoms() {
  const response = await apiClient.get('/api/symptoms/');
  return response.data;
}

export async function getSymptomsByDate(date) {
  const response = await apiClient.get(`/api/symptoms/date/${date}`);
  return response.data;
}

export async function createSymptom(data) {
  const response = await apiClient.post('/api/symptoms/', data);
  return response.data;
}

export async function updateSymptom(id, data) {
  const response = await apiClient.put(`/api/symptoms/${id}`, data);
  return response.data;
}

export async function deleteSymptom(id) {
  const response = await apiClient.delete(`/api/symptoms/${id}`);
  return response.data;
}
