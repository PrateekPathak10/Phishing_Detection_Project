import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Import the Tailwind base styles
// Import your main application component
import App from './PhishingDetectionDashboard';

// Use the modern React 18 API for rendering
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
