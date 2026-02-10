import { useState, useEffect } from 'react';
import { User, Bell, Key, Globe, Save } from 'lucide-react';
import Header from '../components/layout/Header.tsx';
import { getJurisdictions } from '../services/regulatoryService.ts';

export default function Settings() {
    const [emailNotifications, setEmailNotifications] = useState(true);
    const [smsNotifications, setSmsNotifications] = useState(false);
    // Mock data used here
    const [apiKey, setApiKey] = useState('sk-********************xyz');
    const [userName, setUserName] = useState('Super Admin');
    const [userEmail, setUserEmail] = useState('superadmin@legalguard.com');

    const [jurisdiction, setJurisdiction] = useState('');
    const [jurisdictions, setJurisdictions] = useState<{ code: string; name: string }[]>([]);

    const handleSaveSettings = () => {
        console.log('Saving settings:', {
        jurisdiction,
        emailNotifications,
        smsNotifications,
        userName,
        userEmail,
        });
        alert('Settings saved successfully!');
    };

    const handleGenerateApiKey = () => {
        const newKey = `sk-${Math.random().toString(36).slice(2)}${Math.random().toString(36).slice(2)}`;
        setApiKey(newKey);
        alert('New API key generated!');
    };

    const handleCopyApiKey = () => {
        const el = document.createElement('textarea');
        el.value = apiKey;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('API Key copied to clipboard!');
    };

    useEffect(() => {
            const fetchJurisdictions = async () => {
                try {
                    const response = await getJurisdictions();
                    console.log("Fetched jurisdictions:", response);

                    const codes: string[] = response?.data?.jurisdictions ?? [];

                    const JURISDICTION_NAMES: Record<string, string> = {
                        MY: 'Malaysia',
                        SG: 'Singapore',
                        EU: 'European Union',
                        US: 'United States'
                    };

                    const formatted = codes.map(code => ({
                        code,
                        name: JURISDICTION_NAMES[code] || code,
                    }));

                    setJurisdictions(formatted);
                } catch (error) {
                    console.error('Failed to fetch jurisdictions:', error);
                }
            };

            fetchJurisdictions();
        }, []);

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans">
        <Header />

        <main className="max-w-4xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
            <h1 className="text-4xl font-extrabold text-white mb-8 text-center">Settings & Configuration</h1>

            {/* User profile section */}
            <section className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-8 shadow-xl">
            <h2 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                <User className="w-6 h-6" /> User Profile
            </h2>
            <div className="space-y-4">
                <div>
                <label htmlFor="user-name" className="block text-sm text-gray-300 mb-1">Full Name</label>
                <input
                    id="user-name"
                    type="text"
                    className="w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                />
                </div>
                <div>
                <label htmlFor="user-email" className="block text-sm text-gray-300 mb-1">Email Address</label>
                <input
                    id="user-email"
                    type="email"
                    className="w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-700 text-gray-200 focus:ring-2 focus:ring-blue-500"
                    value={userEmail}
                    onChange={(e) => setUserEmail(e.target.value)}
                />
                </div>
            </div>
            </section>

            {/* Default jurisdiction - select */}
            <section className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-8 shadow-xl">
            <h2 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                <Globe className="w-6 h-6" /> Default Jurisdiction
            </h2>
            <label htmlFor="default-jurisdiction" className="block text-sm text-gray-300 mb-1">
                Preferred Jurisdiction for Analysis
            </label>
            <select
                    value={jurisdiction}
                    onChange={(e) => setJurisdiction(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-700 text-gray-200"
                    >
                    <option value="">Select jurisdiction</option>
                    {jurisdictions.map((j) => (
                        <option key={j.code} value={j.code}>
                        {j.name}
                        </option>
                    ))}
            </select>
            </section>

            {/* Notification preferences - email or sms??? */}
            <section className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-8 shadow-xl">
            <h2 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                <Bell className="w-6 h-6" /> Notification Preferences
            </h2>
            <div className="space-y-3">
                <div className="flex items-center">
                <input
                    id="email-notifications"
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 border-gray-600 rounded"
                    checked={emailNotifications}
                    onChange={(e) => setEmailNotifications(e.target.checked)}
                />
                <label htmlFor="email-notifications" className="ml-2 text-sm text-gray-300">Email Notifications</label>
                </div>
                <div className="flex items-center">
                <input
                    id="sms-notifications"
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 border-gray-600 rounded"
                    checked={smsNotifications}
                    onChange={(e) => setSmsNotifications(e.target.checked)}
                />
                <label htmlFor="sms-notifications" className="ml-2 text-sm text-gray-300">SMS Notifications</label>
                </div>
            </div>
            </section>

            {/* API Key management */}
            <section className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-8 shadow-xl">
            <h2 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                <Key className="w-6 h-6" /> API Key Management
            </h2>
            <div className="space-y-4">
                <div>
                <label htmlFor="api-key" className="block text-sm text-gray-300 mb-1">Your API Key</label>
                <div className="flex">
                    <input
                    id="api-key"
                    type="text"
                    className="flex-grow rounded-l-md px-3 py-2 border border-slate-600 bg-slate-700 text-gray-200"
                    value={apiKey}
                    readOnly
                    />
                    <button
                    onClick={handleCopyApiKey}
                    className="px-4 py-2 rounded-r-md bg-slate-600 hover:bg-slate-500 border border-l-0 border-slate-600 text-gray-200 text-sm"
                    >
                    Copy
                    </button>
                </div>
                </div>
                <p className="text-sm text-gray-400">Use this key for third-party integrations.</p>
                <button
                onClick={handleGenerateApiKey}
                className="bg-blue-700 hover:bg-blue-800 text-white py-2 px-6 rounded-md shadow-md transition hover:scale-105"
                >
                Generate New Key
                </button>
            </div>
            </section>

            <div className="text-center mt-10">
            <button
                onClick={handleSaveSettings}
                className="bg-purple-700 hover:bg-purple-800 text-white font-bold py-3 px-10 rounded-lg shadow-xl transition-all transform hover:scale-105 flex items-center gap-2 mx-auto"
            >
                <Save className="w-6 h-6" /> Save All Settings
            </button>
            </div>
        </main>
        </div>
    );
}
