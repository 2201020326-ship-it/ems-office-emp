import axios from "axios";

const TOKEN_KEY = "ems_token";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

export const getApiErrorMessage = (error, fallback = "Request failed") => {
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }

  if (error?.message) {
    return error.message;
  }

  return fallback;
};

export const tokenStorage = {
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  get: () => localStorage.getItem(TOKEN_KEY),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export default api;
