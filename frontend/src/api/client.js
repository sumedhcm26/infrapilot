/**
 * API Client
 * ==========
 * Centralized HTTP client for all API calls.
 * Using axios with a base URL means we only define the server address once.
 *
 * The BASE_URL points to the backend server.
 * In production (Vercel), set VITE_API_URL env var to your Render backend URL.
 */

import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 second timeout
})

// Request interceptor - runs before every request
api.interceptors.request.use(
  (config) => {
    // You could add auth tokens here:
    // const token = localStorage.getItem('token')
    // if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - runs after every response
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Centralized error handling
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    console.error('API Error:', message)
    return Promise.reject(new Error(message))
  }
)

// ------------------------------------------------
// Services API
// ------------------------------------------------
export const servicesApi = {
  list: (params) => api.get('/api/v1/services/', { params }),
  create: (data) => api.post('/api/v1/services/', data),
  get: (id) => api.get(`/api/v1/services/${id}`),
  update: (id, data) => api.patch(`/api/v1/services/${id}`, data),
  delete: (id) => api.delete(`/api/v1/services/${id}`),
  check: (id) => api.post(`/api/v1/services/${id}/check`),
  summary: () => api.get('/api/v1/services/stats/summary'),
}

// ------------------------------------------------
// Deployments API
// ------------------------------------------------
export const deploymentsApi = {
  list: (params) => api.get('/api/v1/deployments/', { params }),
  create: (data) => api.post('/api/v1/deployments/', data),
  get: (id) => api.get(`/api/v1/deployments/${id}`),
  update: (id, data) => api.patch(`/api/v1/deployments/${id}`, data),
}

// ------------------------------------------------
// Incidents API
// ------------------------------------------------
export const incidentsApi = {
  list: (params) => api.get('/api/v1/incidents/', { params }),
  create: (data) => api.post('/api/v1/incidents/', data),
  get: (id) => api.get(`/api/v1/incidents/${id}`),
  update: (id, data) => api.patch(`/api/v1/incidents/${id}`, data),
}

// ------------------------------------------------
// Environments API
// ------------------------------------------------
export const environmentsApi = {
  list: () => api.get('/api/v1/environments/'),
  create: (data) => api.post('/api/v1/environments/', data),
  delete: (id) => api.delete(`/api/v1/environments/${id}`),
}

// ------------------------------------------------
// Health Check
// ------------------------------------------------
export const healthApi = {
  check: () => api.get('/health'),
}

export default api
