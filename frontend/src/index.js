import React from 'react';
import { createRoot } from 'react-dom/client';
import PhishingDetectionDashboard from './PhishingDetectionDashboard.jsx';
import './index.css';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(
    <React.StrictMode>
        <PhishingDetectionDashboard />
    </React.StrictMode>
);