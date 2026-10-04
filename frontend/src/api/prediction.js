/**
 * Prediction API service for Milestone 2 ML Engine
 */
import apiClient from './client';

export const getPrediction = async (data) => {
  const response = await apiClient.post('/predict', data);
  return response.data;
};

export const getPredictionFromApp = async (appData) => {
  const response = await apiClient.post('/predict/from-app', appData);
  return response.data;
};
