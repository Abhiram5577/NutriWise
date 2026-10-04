/**
 * Auth API functions — register, login, and get current user.
 */
import apiClient from './client';

export async function registerUser({ name, email, username, password }) {
  const response = await apiClient.post('/api/auth/register', {
    name,
    email,
    username,
    password,
  });
  return response.data;
}

export async function loginUser({ email, password }) {
  const response = await apiClient.post('/api/auth/login', {
    email,
    password,
  });
  return response.data;
}

export async function getCurrentUser(token) {
  const response = await apiClient.get('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}
