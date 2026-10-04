/**
 * Nutrition API — external food database search.
 */
import apiClient from './client';

export async function searchNutrition(query, limit = 10) {
  const response = await apiClient.get('/api/nutrition/search', {
    params: { query, limit },
  });
  return response.data;
}
