import React, { useState, useEffect, useCallback } from 'react';

// NOTE ON BACKEND: 
// This URL assumes your Flask app.py is running on the default port 5000.
const API_BASE_URL = 'http://127.0.0.1:5000'; 

// --- MOCK DATA FOR DEMONSTRATION & UI ---
const CRITICAL_SECTORS = [
    { name: "Airtel", domain: "airtel.in" },
    { name: "State Bank of India (SBI)", domain: "sbi.co.in" },
    { name: "HDFC Bank", domain: "hdfcbank.com" },
    { name: "ICICI Bank", domain: "icicibank.com" },
];

const LABEL_COLORS = {
    0: { text: "Legitimate (0)", color: "text-green-600", bg: "bg-green-100" },
    1: { text: "Suspected (1)", color: "text-yellow-600", bg: "bg-yellow-100" },
    2: { text: "Phishing (2)", textDanger: "text-red-700 font-bold", color: "text-red-500", bg: "bg-red-100" },
};

// --- MOCK DATABASE AND MONITORING LOGIC (Replacing Firestore for single-file deployment) ---
// In a real deployment, the backend would manage this data persistence.
let MONITORING_DB = JSON.parse(localStorage.getItem('MONITORING_DB_MOCK')) || [];

const saveMockDB = (newDb) => {
    MONITORING_DB = newDb;
    localStorage.setItem('MONITORING_DB_MOCK', JSON.stringify(newDb));
};

// --- 1. Main App Component ---
const App = () => {
    const [domainInput, setDomainInput] = useState('');
    const [cseDomain, setCseDomain] = useState(CRITICAL_SECTORS[0].domain);
    const [cseName, setCseName] = useState(CRITICAL_SECTORS[0].name);
    const [results, setResults] = useState(MONITORING_DB);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedReport, setSelectedReport] = useState(null);
    const [systemAlert, setSystemAlert] = useState(null);

    // --- 2. Suspected Domain Monitoring Cycle (Simulated Backend Cron Job) ---
    // This effect simulates the continuous monitoring engine (Requirement 3.3).
    useEffect(() => {
        const checkMonitoring = () => {
            let updatedResults = [...MONITORING_DB];
            let alertTriggered = false;

            updatedResults = updatedResults.map(item => {
                // Only monitor domains currently classified as Suspected (1)
                if (item.prediction_id === 1 && item.monitoring.status === 'Monitoring') {
                    // SIMULATION: 1 in 10 chance of reclassification to Phishing
                    if (Math.random() < 0.1) {
                        alertTriggered = true;
                        
                        // Update status and reclassify (Label 2)
                        const now = new Date();
                        const newReport = { ...item.report_data };
                        newReport.final_classification = 'PHISHING (RECLASSIFIED)';
                        newReport.classification_id = 2;
                        newReport.maliciousness_information.reclassification_details = `Content change detected on Day ${Math.ceil(item.monitoring.daysElapsed)}`;

                        return {
                            ...item,
                            prediction_id: 2,
                            label: 'Phishing (Reclassified)',
                            report_data: newReport,
                            monitoring: { ...item.monitoring, status: 'RECLASSIFIED' }
                        };
                    }
                }
                // Update elapsed time
                if (item.monitoring.status === 'Monitoring') {
                    item.monitoring.daysElapsed += 0.1; // Simulate partial day check
                    if (item.monitoring.daysElapsed >= 90) {
                        item.monitoring.status = 'COMPLETED (Timed Out)';
                    }
                }
                return item;
            });

            if (alertTriggered) {
                setSystemAlert('🚨 URGENT: One or more suspected domains have been reclassified as PHISHING after dynamic content monitoring!');
            }
            saveMockDB(updatedResults);
            setResults(updatedResults);
        };

        const interval = setInterval(checkMonitoring, 10000); // Runs every 10 seconds

        return () => clearInterval(interval); // Cleanup on unmount
    }, []);

    // --- 3. API Communication Function ---
    const handleDomainCheck = async (e) => {
        e.preventDefault();
        if (!domainInput) return;

        setIsLoading(true);
        setSystemAlert(null);

        try {
            const response = await fetch(`${API_BASE_URL}/api/classify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    domain: domainInput, 
                    cse_domain: cseDomain, 
                    cse_name: cseName 
                }),
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();
            
            const newEntry = {
                id: Date.now(),
                domain: domainInput,
                prediction_id: data.prediction_id,
                label: data.label,
                report_data: data.report_data,
                monitoring: {
                    status: data.prediction_id === 1 ? 'Monitoring' : 'N/A',
                    daysElapsed: 0,
                    startDate: new Date().toLocaleDateString(),
                }
            };
            
            const updatedResults = [newEntry, ...MONITORING_DB];
            saveMockDB(updatedResults);
            setResults(updatedResults);
            setDomainInput('');

            if (data.prediction_id === 2) {
                setSystemAlert(`🔴 ALERT: ${domainInput} classified as PHISHING.`);
            }

        } catch (error) {
            setSystemAlert(`Error contacting backend: ${error.message}. Ensure Flask server is running at ${API_BASE_URL}.`);
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    // --- 4. Render Helper Functions ---

    const getStatusDisplay = (item) => {
        const { prediction_id, label, monitoring } = item;
        const color = LABEL_COLORS[prediction_id]?.bg || 'bg-gray-200';
        const textColor = LABEL_COLORS[prediction_id]?.color || 'text-gray-800';

        if (prediction_id === 1 && monitoring.status === 'Monitoring') {
            return (
                <span className="flex items-center text-sm font-medium text-yellow-700">
                    <span className="relative flex h-3 w-3 mr-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-yellow-500"></span>
                    </span>
                    Monitoring ({Math.ceil(monitoring.daysElapsed)} days)
                </span>
            );
        }
        if (monitoring.status === 'RECLASSIFIED') {
            return <span className="text-sm font-bold text-red-700">RECLASSIFIED (Phishing)</span>;
        }

        return <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${color} ${textColor}`}>{label}</span>;
    };

    // --- 5. UI Structure ---

    return (
        <div className="min-h-screen bg-gray-50 p-4 sm:p-8 font-sans">
            <script src="https://cdn.tailwindcss.com"></script>
            <div className="max-w-6xl mx-auto">
                <header className="mb-8 p-6 bg-white rounded-xl shadow-lg">
                    <h1 className="text-4xl font-extrabold text-indigo-800 mb-2">AI Grand Challenge 2025: Phishing Engine</h1>
                    <p className="text-gray-600">Scalable, efficient, automated detection and monitoring of Phishing and Suspected domains for Critical Sector Entities (CSEs).</p>
                    <div className="mt-4 border-t pt-4">
                        <p className="text-sm font-medium text-gray-500">System Status:</p>
                        {systemAlert ? (
                            <div className="mt-2 p-3 rounded-lg bg-red-100 border border-red-400 text-red-800 font-semibold text-sm animate-pulse">{systemAlert}</div>
                        ) : (
                            <div className="mt-2 text-sm text-green-700 font-semibold">Backend connection stable. Monitoring cycle running every 10s.</div>
                        )}
                    </div>
                </header>

                {/* Domain Input Form */}
                <section className="mb-8 p-6 bg-white rounded-xl shadow-lg border-t-4 border-indigo-500">
                    <h2 className="text-2xl font-semibold text-gray-800 mb-4">Analyze New Domain</h2>
                    <form onSubmit={handleDomainCheck} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label htmlFor="domain" className="block text-sm font-medium text-gray-700">Domain to Check</label>
                                <input
                                    type="text"
                                    id="domain"
                                    value={domainInput}
                                    onChange={(e) => setDomainInput(e.target.value)}
                                    placeholder="e.g., airtel-support.in"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
                                    required
                                />
                            </div>
                            <div>
                                <label htmlFor="cseDomain" className="block text-sm font-medium text-gray-700">Target CSE</label>
                                <select
                                    id="cseDomain"
                                    value={cseDomain}
                                    onChange={(e) => {
                                        const selectedCse = CRITICAL_SECTORS.find(c => c.domain === e.target.value);
                                        setCseDomain(selectedCse.domain);
                                        setCseName(selectedCse.name);
                                    }}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border bg-white"
                                >
                                    {CRITICAL_SECTORS.map((cse, index) => (
                                        <option key={index} value={cse.domain}>{cse.name} ({cse.domain})</option>
                                    ))}
                                </select>
                            </div>
                            <div className="self-end">
                                <button
                                    type="submit"
                                    className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isLoading ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150'}`}
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Analyzing...' : 'Run AI Classification'}
                                </button>
                            </div>
                        </div>
                    </form>
                </section>

                {/* Results Table (Requirement 3.1) */}
                <section className="bg-white rounded-xl shadow-lg overflow-hidden">
                    <h2 className="text-2xl font-semibold text-gray-800 p-6 border-b">Detection Results ({results.length} Total)</h2>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Domain</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Target CSE</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Classification</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status/Monitoring</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {results.length === 0 ? (
                                    <tr><td colSpan="5" className="px-6 py-4 text-center text-gray-500">No domains analyzed yet.</td></tr>
                                ) : (
                                    results.map((item) => (
                                        <tr key={item.id} className={item.prediction_id === 2 || item.monitoring.status === 'RECLASSIFIED' ? 'bg-red-50/50' : ''}>
                                            <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${item.prediction_id === 2 ? 'text-red-700 font-bold' : 'text-gray-900'}`}>{item.domain}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.report_data.genuine_cse_domain}</td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={LABEL_COLORS[item.prediction_id]?.textDanger || LABEL_COLORS[item.prediction_id]?.color}>
                                                    {item.label}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">{getStatusDisplay(item)}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button
                                                    onClick={() => setSelectedReport(item)}
                                                    className="text-indigo-600 hover:text-indigo-900 font-semibold"
                                                >
                                                    View Report
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </section>
                
                {selectedReport && (
                    <ReportModal report={selectedReport} onClose={() => setSelectedReport(null)} />
                )}
            </div>
        </div>
    );
};

// --- 6. Report Modal Component (Requirement 3.4) ---
const ReportModal = ({ report, onClose }) => {
    const data = report.report_data;
    const confidence = data.maliciousness_information.model_confidence;

    const sections = [
        {
            title: "Classification & Confidence (AI Engine)",
            items: [
                { label: "Final Classification", value: data.final_classification, color: LABEL_COLORS[data.classification_id]?.textDanger || LABEL_COLORS[data.classification_id]?.color },
                { label: "Legitimate Confidence", value: `${(parseFloat(confidence.legitimate_score) * 100).toFixed(2)}%`, barColor: 'bg-green-500' },
                { label: "Suspected Confidence", value: `${(parseFloat(confidence.suspected_score) * 100).toFixed(2)}%`, barColor: 'bg-yellow-500' },
                { label: "Phishing Confidence", value: `${(parseFloat(confidence.phishing_score) * 100).toFixed(2)}%`, barColor: 'bg-red-500' },
                { label: "Reclassification Details", value: data.maliciousness_information.reclassification_details },
            ]
        },
        {
            title: "Domain Attributes (Requirement 3.4)",
            items: [
                { label: "Domain Creation Date", value: data.domain_attributes.creation_date_time },
                { label: "Registrar Information", value: data.domain_attributes.registrar_info },
                { label: "Privacy Protected", value: data.domain_attributes.is_privacy_protected ? 'Yes' : 'No' },
            ]
        },
        {
            title: "Network Attributes (IP/Subnet)",
            items: [
                { label: "IP Address", value: data.network_attributes.ip_address },
                { label: "Subnet Information", value: data.network_attributes.subnet_info },
                { label: "Geo-Location", value: data.network_attributes.geo_location },
                { label: "IP Reputation Score", value: data.network_attributes.ip_reputation_score },
            ]
        }
    ];

    return (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-75 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto transform transition-all">
                <div className="p-6 border-b flex justify-between items-center sticky top-0 bg-white">
                    <h3 className="text-2xl font-bold text-gray-900">
                        Detection Report: <span className="text-indigo-600">{report.domain}</span>
                    </h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-3xl font-light">
                        &times;
                    </button>
                </div>
                
                <div className="p-6 space-y-6">
                    <p className="text-sm text-gray-500 mb-4">Report ID: {data.report_id} | Analysis Time: {new Date(data.analysis_timestamp).toLocaleString()}</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {sections.map((section, index) => (
                            <div key={index} className="bg-gray-50 p-4 rounded-lg shadow-inner">
                                <h4 className="text-lg font-semibold text-indigo-700 border-b pb-2 mb-3">{section.title}</h4>
                                <dl className="space-y-2">
                                    {section.items.map((item, i) => (
                                        <div key={i} className="flex flex-col">
                                            <dt className="text-sm font-medium text-gray-700">{item.label}:</dt>
                                            <dd className={`ml-0 text-md font-mono ${item.color || 'text-gray-900'}`}>{item.value}</dd>
                                        </div>
                                    ))}
                                </dl>
                            </div>
                        ))}
                    </div>
                    
                </div>
            </div>
        </div>
    );
};

export default App;
