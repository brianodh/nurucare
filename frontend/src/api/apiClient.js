import axios from 'axios';

// Pulls from .env file locally set VITE_API_URL=http://127.0.0.1:8000
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─────────────────────────────────────────────
// AXIOS INTERCEPTOR FOR AUTH TOKEN
// ─────────────────────────────────────────────
const AUTH_STORAGE_KEY = 'nurucare_patient';

apiClient.interceptors.request.use((config) => {
  const stored = localStorage.getItem(AUTH_STORAGE_KEY);
  if (stored) {
    try {
      const user = JSON.parse(stored);
      if (user.access_token) {
        config.headers.Authorization = `Bearer ${user.access_token}`;
      }
    } catch (e) {
      console.warn('Failed to parse stored user', e);
    }
  }
  return config;
});

// ─────────────────────────────────────────────
// HEALTH
// ─────────────────────────────────────────────

/** Check backend is alive */
export const checkHealth = () => apiClient.get('/health');

// ─────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────

/** Nurse login with username and password */
export const nurseLogin = (username, password) =>
  apiClient.post('/api/v1/auth/nurse/login', { username, password }).then(r => r.data);

/** Create anonymous patient session */
export const createPatientSession = () =>
  apiClient.post('/api/v1/auth/patient/session').then(r => r.data);

/** Sign up a new user (patient or nurse) */
export const signup = (userData) =>
  apiClient.post('/api/v1/auth/signup', userData).then(r => r.data);

/** Login a user (patient or nurse) */
export const login = (username, password) =>
  apiClient.post('/api/v1/auth/login', { username, password }).then(r => r.data);

/** Get current authenticated user info */
export const getMe = () => apiClient.get('/api/v1/auth/me').then(r => r.data);

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
  apiClient.post('/api/v1/intake', intakeData).then((r) => {
    const data = r.data;
    // live Render backend returns session_id, local returns profile_id normalise
    return { ...data, profile_id: data.profile_id || data.session_id };
  });

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
// PATIENT PROFILE (dashboard + intake persisted data)
// ─────────────────────────────────────────────

/** Fetch the currently authenticated patient's full profile + safety score.
 *  Response: { success, profile, safety_score: { score, risk_level, flags } }
 */
export const getPatientProfile = () =>
  apiClient.get('/api/v1/patient/profile').then((r) => r.data);

/** Partial update of the patient's profile (e.g. side_effects, BP, etc.)
 *  @param {Partial<{side_effects, duration_pref, age, smoking, migraine_type,
 *    systolic_bp, diastolic_bp, breastfeeding, postpartum_weeks, last_period_date}>} patch
 */
export const updatePatientProfile = (patch) =>
  apiClient.put('/api/v1/patient/profile', patch).then((r) => r.data);

/** Append one side-effect entry to the profile's side_effects jsonb array.
 *  @param {{symptom, severity, started_on, notes?, method?}} entry
 */
export const appendSideEffect = (entry) =>
  apiClient.post('/api/v1/patient/profile/side-effects', entry).then((r) => r.data);

/** Client-side helper for computing a 0-100 safety score from profile flags.
 *  Mirrors database.compute_safety_score so offline dashboards still render real
 *  numbers without a backend fetch.  Never hardcodes a static score.
 */
export const computeSafetyScore = (profile = {}) => {
  if (!profile || typeof profile !== 'object') {
    return { score: 0, risk_level: 'high', flags: ['No profile data yet'] };
  }
  const age = Number(profile.age) || 0;
  const smoking = Boolean(profile.smoking);
  const migraine = profile.migraine_type || 'none';
  const breastfeeding = Boolean(profile.breastfeeding);
  const systolic = Number(profile.systolic_bp) || 0;
  const diastolic = Number(profile.diastolic_bp) || 0;

  const flags = [];
  if (smoking && age > 35)
    flags.push('Age >35 + smoking — WHO MEC Category 4 risk for combined methods');
  if (migraine === 'with_aura')
    flags.push('Migraine with aura — WHO MEC Category 4 risk for combined methods');
  if (migraine === 'without_aura')
    flags.push('Migraine without aura — monitor blood pressure closely with combined methods');
  if (breastfeeding)
    flags.push('Breastfeeding — only progestogen-only methods are recommended in the first 6 weeks');
  if (systolic >= 140 || diastolic >= 90)
    flags.push('Elevated blood pressure — discuss options with a provider before starting combined methods');

  let score = 100;
  if (smoking && age > 35) score -= 40;
  if (migraine === 'with_aura') score -= 30;
  if (migraine === 'without_aura') score -= 8;
  if (breastfeeding) score -= 5;
  if (systolic >= 140 || diastolic >= 90) score -= 12;
  score = Math.max(0, Math.min(100, Math.round(score)));

  const risk_level = score < 60 ? 'high' : score < 85 ? 'medium' : 'low';
  return { score, risk_level, flags };
};

// ─────────────────────────────────────────────
// SESSION KEY  (patient → nurse handoff)
// ─────────────────────────────────────────────

/**
 * Generate a 6-digit session key for nurse access.
 * @param {string} patientId
 * @returns {Promise<{ session_key, expires_in_minutes }>}
 */
export const getDashboardStats = () =>
  apiClient.get('/api/v1/nurse/dashboard').then((r) => r.data).catch(() =>
    apiClient.get('/health').then(() => ({ activeConsultations: 0, riskFlags: 0, dailySessions: 0, recentPatients: [], ageDemographics: [] }))
  );

export const generateSessionKey = (profileId) =>
  apiClient.post('/api/v1/session-key', {
    profile_id: profileId || null,
  }).then((r) => r.data);

/**
 * Nurse: look up patient data by session key.
 * @param {string} sessionKey
 * @returns {Promise<{ success, patient_data } | { success, error }>}
 */
export const getPatientBySessionKey = (sessionKey) =>
  apiClient.post('/api/v1/nurse/verify-session', { session_key: sessionKey }).then((r) => r.data);

// ─────────────────────────────────────────────
// PARTNER SYNC
// ─────────────────────────────────────────────

/**
 * Generate an anonymous partner sync token.
 * @returns {Promise<{ token, expires_in_hours }>}
 */
export const generateSyncToken = (profileId) =>
  apiClient.post('/api/v1/sync/token', { profile_id: profileId || null }).then((r) => r.data);

/**
 * Verify / redeem a partner sync token.
 * @param {string} token - token from partner
 * @param {string} [profileId] - current user's profile id (optional)
 * @returns {Promise<{ success, linked_profile_id, message }>}
 */
export const verifySyncToken = (token, profileId) =>
  apiClient.post('/api/v1/sync/verify', {
    token,
    profile_id: profileId || null,
  }).then((r) => r.data);

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
// LEGACY MOCK kept so nothing crashes
// ─────────────────────────────────────────────
export const base44 = {
  auth: {
    me: async () => ({ id: 'usr_mock_nuru_99', name: 'Dr. Alex Nuru', role: 'nurse' }),
    logout: () => { window.location.reload(); },
    redirectToLogin: () => {},
  },
};
