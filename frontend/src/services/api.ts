import axios from 'axios';

// Allows absolute backend API URL in cross-origin cloud deployments (e.g., Vercel -> Render)
// Falls back to relative '/api/v1' for local dev, Nginx reverse proxies, or Docker
const apiBase = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

const api = axios.create({
  baseURL: `${apiBase}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor injecting JWT Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('fraudshield_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor handling 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('fraudshield_token');
      localStorage.removeItem('fraudshield_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
