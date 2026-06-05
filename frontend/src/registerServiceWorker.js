/*
 * Service Worker Registration
 * Registers the service worker for PWA offline capabilities
 */

// Check if service workers are supported
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('Service Worker registered successfully:', registration.scope);
        
        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          console.log('New service worker found:', newWorker);
          
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              console.log('Update available - refresh to get latest version');
              // Show update notification to user
              if (confirm('A new version is available. Refresh to update?')) {
                window.location.reload();
              }
            }
          });
        });
      })
      .catch((error) => {
        console.error('Service Worker registration failed:', error);
      });
  });
}

// Listen for online/offline events
window.addEventListener('online', () => {
  console.log('App is online');
  // Refresh data when back online
  window.dispatchEvent(new Event('online-status-change'));
});

window.addEventListener('offline', () => {
  console.log('App is offline');
  window.dispatchEvent(new Event('online-status-change'));
});