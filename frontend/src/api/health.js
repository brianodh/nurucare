/**
 * API Connection Health Check Utility
 * 
 * Tests if the backend API is reachable and responsive.
 * Used by the frontend to show connection status to users.
 * 
 * @module api/health
 * @author NuruCare Team
 * @version 1.0.0
 */

// ============================================
// CONFIGURATION
// ============================================

// API Base URL - change this based on environment
// Development: http://localhost:8000
// Production: https://your-api-domain.com
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Timeout in milliseconds (5 seconds)
const CONNECTION_TIMEOUT = 5000;

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Delay execution for specified milliseconds
 * @param {number} ms - Milliseconds to delay
 * @returns {Promise} Promise that resolves after delay
 */
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Format error message for user display
 * @param {Error} error - The error object
 * @returns {string} User-friendly error message
 */
const formatErrorMessage = (error) => {
    if (error.code === 'ECONNREFUSED') {
        return 'Backend server is not running. Please start the server with: cd backend && python main.py';
    }
    if (error.code === 'ETIMEDOUT') {
        return 'Connection timed out. Please check if the backend server is responsive.';
    }
    if (error.response) {
        return `Server responded with status: ${error.response.status}`;
    }
    if (error.message) {
        return error.message;
    }
    return 'Unknown connection error';
};

// ============================================
// MAIN HEALTH CHECK FUNCTIONS
// ============================================

/**
 * Check if the backend API is reachable
 * 
 * @param {Object} options - Configuration options
 * @param {number} options.timeout - Timeout in milliseconds (default: 5000)
 * @param {number} options.retries - Number of retries (default: 3)
 * @returns {Promise<Object>} Health check result
 * 
 * @example
 * const result = await checkBackendHealth();
 * if (result.healthy) {
 *   console.log('Backend is healthy!');
 * } else {
 *   console.error('Backend is down:', result.error);
 * }
 */
export async function checkBackendHealth(options = {}) {
    const timeout = options.timeout || CONNECTION_TIMEOUT;
    const retries = options.retries || MAX_RETRIES;
    
    let lastError = null;
    
    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            // Create abort controller for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            // Make the health check request
            const response = await fetch(`${API_BASE_URL}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                signal: controller.signal,
            });
            
            clearTimeout(timeoutId);
            
            // Parse response
            const data = await response.json();
            
            // Check if response indicates healthy
            const isHealthy = response.ok && (data.status === 'healthy' || data.status === 'ok');
            
            if (isHealthy) {
                console.log(`✅ Backend health check passed (attempt ${attempt})`);
                return {
                    healthy: true,
                    status: response.status,
                    data: data,
                    latency: null, // We don't measure latency in this simple check
                    message: 'Backend API is reachable and healthy',
                    timestamp: new Date().toISOString(),
                };
            }
            
            // If not healthy but server responded, don't retry
            return {
                healthy: false,
                status: response.status,
                data: data,
                message: `Backend responded but reported unhealthy: ${data.message || 'Unknown'}`,
                timestamp: new Date().toISOString(),
            };
            
        } catch (error) {
            lastError = error;
            console.warn(`⚠️ Health check attempt ${attempt}/${retries} failed:`, error.message);
            
            if (attempt < retries) {
                // Wait before retrying
                await delay(RETRY_DELAY_MS);
            }
        }
    }
    
    // All retries failed
    console.error('❌ Backend health check failed after all retries');
    return {
        healthy: false,
        status: null,
        data: null,
        error: {
            code: lastError?.code || 'UNKNOWN_ERROR',
            message: formatErrorMessage(lastError),
        },
        message: 'Unable to connect to backend API. Please ensure the server is running.',
        timestamp: new Date().toISOString(),
    };
}

/**
 * Quick health check (single attempt, no retries)
 * 
 * @returns {Promise<boolean>} True if healthy, false otherwise
 * 
 * @example
 * const isHealthy = await quickHealthCheck();
 * if (!isHealthy) {
 *   showConnectionError();
 * }
 */
export async function quickHealthCheck() {
    const result = await checkBackendHealth({ retries: 1, timeout: 3000 });
    return result.healthy;
}

/**
 * Check if specific API endpoint is reachable
 * 
 * @param {string} endpoint - API endpoint path (e.g., '/api/v1/intake')
 * @param {Object} options - Additional fetch options
 * @returns {Promise<Object>} Endpoint reachability result
 * 
 * @example
 * const result = await checkEndpoint('/api/v1/intake');
 * if (result.reachable) {
 *   console.log('Intake endpoint is reachable');
 * }
 */
export async function checkEndpoint(endpoint, options = {}) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONNECTION_TIMEOUT);
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        return {
            reachable: true,
            status: response.status,
            statusText: response.statusText,
            endpoint: endpoint,
        };
    } catch (error) {
        return {
            reachable: false,
            error: error.message,
            endpoint: endpoint,
        };
    }
}

/**
 * Get detailed connection diagnostics
 * 
 * @returns {Promise<Object>} Diagnostic information
 * 
 * @example
 * const diagnostics = await getConnectionDiagnostics();
 * console.log(diagnostics);
 */
export async function getConnectionDiagnostics() {
    const diagnostics = {
        timestamp: new Date().toISOString(),
        api_url: API_BASE_URL,
        checks: {},
    };
    
    // Check main health endpoint
    const healthResult = await checkBackendHealth({ retries: 1, timeout: 3000 });
    diagnostics.checks.health = {
        healthy: healthResult.healthy,
        message: healthResult.message,
        status: healthResult.status,
    };
    
    // If healthy, check critical endpoints
    if (healthResult.healthy) {
        const endpoints = [
            '/api/v1/intake',
            '/api/v1/recommend',
            '/api/v1/session-key',
        ];
        
        for (const endpoint of endpoints) {
            const result = await checkEndpoint(endpoint);
            diagnostics.checks[endpoint] = result;
        }
    } else {
        diagnostics.checks.error = healthResult.error;
    }
    
    return diagnostics;
}

/**
 * Subscribe to backend health status changes
 * 
 * @param {Function} callback - Function called with health status
 * @param {number} intervalMs - How often to check (default: 30000ms = 30 seconds)
 * @returns {Function} Unsubscribe function
 * 
 * @example
 * const unsubscribe = subscribeToHealthStatus((isHealthy) => {
 *   if (isHealthy) {
 *     setBackendOnline(true);
 *   } else {
 *     setBackendOnline(false);
 *   }
 * });
 * 
 * // Later, when component unmounts:
 * unsubscribe();
 */
export function subscribeToHealthStatus(callback, intervalMs = 30000) {
    let isRunning = true;
    let timeoutId = null;
    
    const check = async () => {
        if (!isRunning) return;
        
        const isHealthy = await quickHealthCheck();
        callback(isHealthy);
        
        // Schedule next check
        timeoutId = setTimeout(check, intervalMs);
    };
    
    // Start checking
    check();
    
    // Return unsubscribe function
    return () => {
        isRunning = false;
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
    };
}

// ============================================
// REACT HOOK (for use in components)
// ============================================

/**
 * React Hook for backend health status
 * 
 * @param {Object} options - Hook options
 * @param {number} options.checkIntervalMs - Check interval in milliseconds
 * @returns {Object} Health status state
 * 
 * @example
 * const { isHealthy, lastChecked, diagnostics } = useBackendHealth();
 * 
 * if (!isHealthy) {
 *   return <ConnectionError message={diagnostics?.message} />;
 * }
 */
export function useBackendHealth(options = {}) {
    // This is designed to be used with React hooks
    // Since we're in a utility file, we export the logic
    // The actual hook should be implemented in the component
    return {
        checkHealth: checkBackendHealth,
        isHealthy: async () => await quickHealthCheck(),
        getDiagnostics: getConnectionDiagnostics,
    };
}

// ============================================
// DEFAULT EXPORT
// ============================================

export default {
    checkBackendHealth,
    quickHealthCheck,
    checkEndpoint,
    getConnectionDiagnostics,
    subscribeToHealthStatus,
    useBackendHealth,
};