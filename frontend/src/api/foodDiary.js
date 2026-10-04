/**
 * Food Diary API — CRUD operations for food diary entries.
 */
import apiClient from './client';

export async function getFoodEntries(skip = 0, limit = 50) {
  const response = await apiClient.get('/api/food-diary/', {
    params: { skip, limit },
  });
  return response.data;
}

export async function getFoodEntriesByDate(dateStr) {
  const response = await apiClient.get(`/api/food-diary/date/${dateStr}`);
  return response.data;
}

export async function getFoodEntry(id) {
  const response = await apiClient.get(`/api/food-diary/${id}`);
  return response.data;
}

export async function createFoodEntry(data) {
  const response = await apiClient.post('/api/food-diary/', data);
  return response.data;
}

export async function updateFoodEntry(id, data) {
  const response = await apiClient.put(`/api/food-diary/${id}`, data);
  return response.data;
}

export async function deleteFoodEntry(id) {
  await apiClient.delete(`/api/food-diary/${id}`);
}
