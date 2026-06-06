/**
 * Connection Status Component
 * Displays backend connection status to the user
 * 
 * @component
 */

import React, { useState, useEffect } from 'react';
import { checkBackendHealth, subscribeToHealthStatus } from '../api/health';

const ConnectionStatus = () => {
    const [isHealthy, setIsHealthy] = useState(null);
    const [isChecking, setIsChecking] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    // Check health on component mount
    useEffect(() => {
        const checkInitialHealth = async () => {
            setIsChecking(true);
            const result = await checkBackendHealth();
            setIsHealthy(result.healthy);
            if (!result.healthy && result.error) {
                setErrorMessage(result.error.message);
            }
            setIsChecking(false);
        };

        checkInitialHealth();

        // Subscribe to periodic health checks
        const unsubscribe = subscribeToHealthStatus((healthy) => {
            setIsHealthy(healthy);
            if (!healthy) {
                setErrorMessage('Backend connection lost. Please check if server is running.');
            } else {
                setErrorMessage('');
            }
        }, 30000); // Check every 30 seconds

        return () => unsubscribe();
    }, []);

    // Determine status display
    const getStatusDisplay = () => {
        if (isChecking && isHealthy === null) {
            return {
                color: 'text-yellow-500',
                icon: '🔄',
                text: 'Connecting to backend...',
            };
        }
        if (isHealthy === true) {
            return {
                color: 'text-green-500',
                icon: '✅',
                text: 'Backend connected',
            };
        }
        if (isHealthy === false) {
            return {
                color: 'text-red-500',
                icon: '❌',
                text: 'Backend offline',
            };
        }
        return {
            color: 'text-gray-500',
            icon: '⚪',
            text: 'Unknown',
        };
    };

    const status = getStatusDisplay();

    return (
        <div className={`flex items-center gap-2 text-sm ${status.color}`}>
            <span>{status.icon}</span>
            <span>{status.text}</span>
            {errorMessage && (
                <span className="text-xs text-red-400 ml-2">
                    ({errorMessage})
                </span>
            )}
        </div>
    );
};

export default ConnectionStatus;