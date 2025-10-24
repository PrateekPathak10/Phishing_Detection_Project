import React, { useState, useEffect } from 'react';
import { RefreshCw, Zap, Shield, HelpCircle, XCircle } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000/api';
const LABEL_COLORS = {
    Legitimate: 'bg-green-100 text-green-800 border-green-400',
    Suspected: 'bg-yellow-100 text-yellow-800 border-yellow-400',
    Phishing: 'bg-red-100 text-red-800 border-red-400',
};

const LABEL_ICONS = {
    Legitimate: Shield,
    Suspected: HelpCircle,
    Phishing: Zap,
};

// --- Helper component to display key data points in the card ---
const DetailItem = ({ label, value, isLink = false }) => {
    // Ensure value is a string before attempting truncation or display
    // Use nullish coalescing to safely default to 'N/A'
    const displayValue = String(value ?? 'N/A');
    const truncatedValue = displayValue.length > 50 ? displayValue.substring(0, 50) + '...' : displayValue;

    return (
        <div className="flex justify-between border-b border-gray-100 py-2">
            <span className="text-sm font-medium text-gray-500">{label}</span>
            {isLink && displayValue !== 'N/A' ? (
                <a 
                    href={displayValue} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-700 truncate max-w-[60%] text-right"
                >
                    {displayValue}
                </a>
            ) : (
                <span className="text-sm font-semibold text-gray-900 truncate max-w-[60%] text-right">
                    {truncatedValue}
                </span>
            )}
        </div>
    );
};


const PhishingDetectionDashboard = () => {
    // State updated to handle full URL input
    const [url, setUrl] = useState('');
    const [cseDomain, setCseDomain] = useState('airtel.in');
    const [cseName, setCseName] = useState('Airtel');
    
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // --- Status Check (Minimal useEffect retained) ---
    useEffect(() => {
    }, []);


    // --- Classification Logic ---
    const handleClassification = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);
        setError(null);

        if (!url || !cseDomain || !cseName) {
            setError("All input fields are required.");
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/classify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Sending 'url' as required by the updated backend API
                body: JSON.stringify({ 
                    url: url.trim(), 
                    cse_domain: cseDomain.trim(), 
                    cse_name: cseName.trim() 
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setResult(data);
            
        } catch (err) {
            console.error("Classification error:", err);
            setError(`Error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    // --- Render Component ---
    
    // Safety checks and destructuring
    const resultIsReady = result && result.report_data;
    const reportData = result?.report_data;
    const submissionData = reportData?.submission_data;
    const confidenceScores = reportData?.maliciousness_information?.model_confidence;
    const finalLabel = result?.label;
    
    // SAFE Logic: Define icon/color defaults to prevent render crash
    const IconComponent = finalLabel ? LABEL_ICONS[finalLabel] : XCircle;
    const labelColorClass = finalLabel 
        ? LABEL_COLORS[finalLabel] 
        : 'bg-gray-100 text-gray-800 border-gray-400';
    
    // Explicitly define text color to avoid complex string manipulation (the crash source)
    let textBaseColor = 'text-gray-800'; 
    if (finalLabel === 'Phishing') textBaseColor = 'text-red-800';
    else if (finalLabel === 'Suspected') textBaseColor = 'text-yellow-800';
    else if (finalLabel === 'Legitimate') textBaseColor = 'text-green-800';


    return (
        <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center">
            <h1 className="text-3xl font-bold text-gray-800 mb-8 flex items-center">
                <Zap className="mr-3 text-red-600" size={28} />
                Phishing Detection Engine (PS-02)
            </h1>

            {/* Input Form */}
            <form onSubmit={handleClassification} className="w-full max-w-2xl bg-white p-6 rounded-xl shadow-lg border border-gray-200 mb-8">
                <div className="space-y-4">
                    {/* URL Input - Updated Label */}
                    <div className="flex flex-col">
                        <label htmlFor="url" className="text-sm font-medium text-gray-700 mb-1">
                            Suspicious URL to Classify (e.g., https://airtel-merchants-app.in/login.php)
                        </label>
                        <input
                            type="text"
                            id="url"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            placeholder="Enter full URL"
                            className="p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                            required
                        />
                    </div>
                    
                    {/* CSE Domain and Name Inputs */}
                    <div className="flex space-x-4">
                        <div className="flex flex-col flex-1">
                            <label htmlFor="cseDomain" className="text-sm font-medium text-gray-700 mb-1">
                                Target CSE Domain (e.g., airtel.in)
                            </label>
                            <input
                                type="text"
                                id="cseDomain"
                                value={cseDomain}
                                onChange={(e) => setCseDomain(e.target.value)}
                                placeholder="Target CSE Domain"
                                className="p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                                required
                            />
                        </div>
                        <div className="flex flex-col flex-1">
                            <label htmlFor="cseName" className="text-sm font-medium text-gray-700 mb-1">
                                Target CSE Name (e.g., Airtel)
                            </label>
                            <input
                                type="text"
                                id="cseName"
                                value={cseName}
                                onChange={(e) => setCseName(e.target.value)}
                                placeholder="Target CSE Name"
                                className="p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition duration-150"
                                required
                            />
                        </div>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full mt-6 p-3 rounded-lg font-semibold text-white transition duration-150 ${
                        loading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-md'
                    }`}
                >
                    {loading ? (
                        <span className="flex items-center justify-center">
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Analyzing URL...
                        </span>
                    ) : (
                        'Run Phishing Check'
                    )}
                </button>
            </form>

            {/* Error Message */}
            {error && (
                <div className="w-full max-w-2xl p-4 mb-8 bg-red-50 border border-red-300 rounded-lg text-red-700">
                    <strong>Error:</strong> {error}
                </div>
            )}

            {/* Results Display - Conditional rendering based on resultIsReady */}
            {resultIsReady && (
                <div className="w-full max-w-3xl">
                    <div className={`p-5 rounded-xl shadow-xl ${labelColorClass} border-l-4 mb-6`}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <IconComponent size={24} className={`w-6 h-6 ${textBaseColor}`} />
                                <h2 className="text-xl font-bold">
                                    Final Classification: {finalLabel}
                                </h2>
                            </div>
                            <span className="text-sm font-mono opacity-80">ID: {result.prediction_id}</span>
                        </div>
                        <p className={`mt-2 text-sm ${textBaseColor}`}>
                            {finalLabel === 'Phishing' ? 'URGENT: Initiate takedown and reporting procedures.' :
                             finalLabel === 'Suspected' ? 'ALERT: Domain will be added to the monitoring engine.' :
                             'SAFE: No immediate threat detected.'}
                        </p>
                    </div>

                    {/* Detailed Report Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        
                        {/* 1. Core Prediction & CSE Mapping */}
                        <div className="bg-white p-5 rounded-xl shadow-md border border-gray-100">
                            <h3 className="text-lg font-semibold text-gray-800 mb-3 border-b pb-2">Prediction Confidence</h3>
                            <DetailItem label="Target URL" value={submissionData?.identified_domain_name} isLink={true} />
                            <DetailItem label="Target CSE" value={submissionData?.critical_sector_entity} />
                            <DetailItem label="Legitimate Score" value={confidenceScores?.legitimate_score} />
                            <DetailItem label="Suspected Score" value={confidenceScores?.suspected_score} />
                            <DetailItem label="Phishing Score" value={confidenceScores?.phishing_score} />
                        </div>
                        
                        {/* 2. WHOIS/Registration Data (Annexure B) */}
                        <div className="bg-white p-5 rounded-xl shadow-md border border-gray-100">
                            <h3 className="text-lg font-semibold text-gray-800 mb-3 border-b pb-2">Registration Details (WHOIS)</h3>
                            <DetailItem label="Registration Date" value={submissionData?.domain_registration_date?.split(' ')[0]} />
                            <DetailItem label="Registrar Name" value={submissionData?.registrar_name} />
                            <DetailItem label="Registrant Org/Name" value={submissionData?.registrant_name_org} />
                            <DetailItem label="Registrant Country" value={submissionData?.registrant_country} />
                            {/* Safest check for deeply nested attribute */}
                            <DetailItem label="Privacy Protected" value={reportData?.domain_attributes?.is_privacy_protected ? 'Yes' : 'No'} />
                        </div>

                        {/* 3. Network/Hosting Data (Annexure B) */}
                        <div className="bg-white p-5 rounded-xl shadow-md border border-gray-100">
                            <h3 className="text-lg font-semibold text-gray-800 mb-3 border-b pb-2">Network & Hosting Details</h3>
                            <DetailItem label="Hosting IP" value={submissionData?.hosting_ip} />
                            <DetailItem label="Hosting ISP" value={submissionData?.hosting_isp} />
                            <DetailItem label="Hosting Country" value={submissionData?.hosting_country} />
                            <DetailItem label="Name Servers" value={submissionData?.name_servers} />
                            <DetailItem label="DNS Records (A, MX)" value={submissionData?.dns_records} />
                        </div>

                        {/* 4. Monitoring & Detection Details */}
                        <div className="bg-white p-5 rounded-xl shadow-md border border-gray-100">
                            <h3 className="text-lg font-semibold text-gray-800 mb-3 border-b pb-2">Detection Metadata</h3>
                            <DetailItem label="Source" value={submissionData?.source_of_detection} />
                            <DetailItem label="Detection Date/Time" value={submissionData?.date_of_detection && submissionData?.time_of_detection ? `${submissionData.date_of_detection} ${submissionData.time_of_detection}` : 'N/A'} />
                            <DetailItem label="Application ID" value={submissionData?.application_id} />
                            <DetailItem label="Reclassification Status" value={reportData?.maliciousness_information?.reclassification_details === 'N/A' ? 'Initial Scan' : 'Reclassified'} />
                            <DetailItem label="Remarks/Reason" value={submissionData?.remarks ?? "N/A"} />
                        </div>
                        
                    </div>
                </div>
            )}
        </div>
    );
};

export default PhishingDetectionDashboard;