import axios from 'axios';

// Pulls from a .env file locally, or defaults to standard FastAPI local address
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock export to prevent crashing if other files still reference the old "base44" name
export const base44 = {
  auth: {
    me: async () => ({ id: "usr_mock_nuru_99", name: "Dr. Alex Nuru", role: "nurse" }),
    logout: () => { window.location.reload(); },
    redirectToLogin: () => {}
  }
};
