import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi } from 'lucide-react';

export default function OfflineBanner() {
  const [online, setOnline] = useState(navigator.onLine);
  const [showRestored, setShowRestored] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setOnline(true);
      setShowRestored(true);
      setTimeout(() => setShowRestored(false), 3000);
    };
    const handleOffline = () => {
      setOnline(false);
      setShowRestored(false);
    };
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (online && !showRestored) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className={`fixed bottom-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2.5 rounded-full text-sm font-medium shadow-lg transition-all duration-300 ${
        online
          ? 'bg-green-500 text-white'
          : 'bg-destructive text-white'
      }`}
    >
      {online ? (
        <>
          <Wifi className="w-4 h-4 flex-shrink-0" />
          <span>Back online · Syncing data…</span>
        </>
      ) : (
        <>
          <WifiOff className="w-4 h-4 flex-shrink-0" />
          <span>Offline · Data saved locally</span>
        </>
      )}
    </div>
  );
}