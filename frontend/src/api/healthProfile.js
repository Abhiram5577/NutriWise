/**
 * Health Profile API — get, create, and update the user's health profile.
 */
import apiClient from './client';

export async function getHealthProfile() {
  const response = await apiClient.get('/api/health-profile/');
  return response.data;
}

export async function createHealthProfile(data) {
  const response = await apiClient.post('/api/health-profile/', data);
  return response.data;
}

export async function updateHealthProfile(data) {
  const response = await apiClient.put('/api/health-profile/', data);
  return response.data;
}
