import axios from 'axios';

// Pulls from .env file locally — set VITE_API_URL=http://127.0.0.1:8000
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─────────────────────────────────────────────
// HEALTH
// ─────────────────────────────────────────────

/** Check backend is alive */
export const checkHealth = () => apiClient.get('/health');

// ─────────────────────────────────────────────
// INTAKE & RECOMMENDATIONS
// ─────────────────────────────────────────────

/**
 * Submit patient intake data.
 * @param {Object} intakeData - shape: { age, gender, systolic_bp, diastolic_bp,
 *   smoking, migraine_type, is_pregnant, breastfeeding, fertility_intention, parity }
 * @returns {Promise<{ success, message, session_id }>}
 */
export const submitIntake = (intakeData) =>
  apiClient.post('/api/v1/intake', intakeData).then((r) => r.data);

/**
 * Get AI-powered contraceptive recommendations.
 * Accepts the same shape as submitIntake.
 * @returns {Promise<{ recommended_methods, restricted_methods,
 *   requires_provider_consultation, general_advice, timestamp,
 *   swahili_version, full_ai_response }>}
 */
export const getRecommendations = (intakeData) =>
  apiClient.post('/api/v1/recommend', intakeData).then((r) => r.data);

// ─────────────────────────────────────────────
// SESSION KEY  (patient → nurse handoff)
// ─────────────────────────────────────────────

/**
 * Generate a 6-digit session key for nurse access.
 * @param {string} patientId
 * @returns {Promise<{ session_key, expires_in_minutes }>}
 */
export const getDashboardStats = () =>
  apiClient.get('/api/v1/nurse/dashboard').then((r) => r.data);

export const generateSessionKey = (patientId) =>
  apiClient.post('/api/v1/session-key', { patient_id: patientId }).then((r) => r.data);

/**
 * Nurse: look up patient data by session key.
 * @param {string} sessionKey
 * @returns {Promise<{ success, patient_data, expires_at } | { success, error }>}
 */
export const getPatientBySessionKey = (sessionKey) =>
  apiClient.post('/api/v1/nurse/patient', null, { params: { session_key: sessionKey } }).then((r) => r.data);

// ─────────────────────────────────────────────
// PARTNER SYNC
// ─────────────────────────────────────────────

/**
 * Generate an anonymous partner sync token.
 * @returns {Promise<{ token, expires_in_hours }>}
 */
export const generateSyncToken = () =>
  apiClient.post('/api/v1/sync/token').then((r) => r.data);

/**
 * Verify / redeem a partner sync token.
 * @param {string} token - token from partner
 * @param {string} yourId - current user's id (can be anonymous uuid)
 * @returns {Promise<{ success, partner_id, message }>}
 */
export const verifySyncToken = (token, yourId) =>
  apiClient.post('/api/v1/sync/verify', { token, your_id: yourId }).then((r) => r.data);

// ─────────────────────────────────────────────
// TRANSLATE
// ─────────────────────────────────────────────

/**
 * Translate text to Swahili (or another language).
 * @param {string} text
 * @param {string} [targetLanguage='swahili']
 * @returns {Promise<{ original, translated, language }>}
 */
export const translateText = (text, targetLanguage = 'swahili') =>
  apiClient.post('/api/v1/translate', { text, target_language: targetLanguage }).then((r) => r.data);

// ─────────────────────────────────────────────
// LEGACY MOCK — kept so nothing crashes
// ─────────────────────────────────────────────
export const base44 = {
  auth: {
    me: async () => ({ id: 'usr_mock_nuru_99', name: 'Dr. Alex Nuru', role: 'nurse' }),
    logout: () => { window.location.reload(); },
    redirectToLogin: () => {},
  },
};
