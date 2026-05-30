import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

import './index.css'

// 🚀 HACKATHON CONSOLE CLEANER
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  const originalError = console.error;
  const originalWarn = console.warn;

  console.error = (...args) => {
    const message = args.join(' ');
    if (message.includes('Base44 SDK Error') || message.includes('/api/apps/') || message.includes('404') || message.includes('StacksProvider')) {
      return; 
    }
    originalError.apply(console, args);
  };

  console.warn = (...args) => {
    const message = args.join(' ');
    if (message.includes('unsupported MIME type') || message.includes('Manifest') || message.includes('apple-mobile-web-app-capable')) {
      return; 
    }
    originalWarn.apply(console, args);
  };
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
