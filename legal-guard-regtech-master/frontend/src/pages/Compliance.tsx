import { AlertCircle, TrendingUp, TrendingDown, CheckSquare, BarChart2, PieChart, Info, Globe, Calendar } from 'lucide-react';
import Header from '../components/layout/Header.tsx';
import { complianceChecklist } from '../data/complianceRequirements';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, Legend } from 'recharts';
interface JurisdictionOverview {
    code: string;
    name: string;
    complianceRate: number;
    pendingAlerts: number;
    trend: 'up' | 'down' | 'stable';
}
interface ComplianceTrendData {
    month: string;
    complianceRate: number;
    criticalAlerts: number;
}
interface RiskDistribution {
    type: 'High Risk' | 'Medium Risk' | 'Low Risk';
    count: number;
    color: string;
}

// Mock data
const mockJurisdictions: JurisdictionOverview[] = [
    { code: 'MY', name: 'Malaysia', complianceRate: 85, pendingAlerts: 3, trend: 'up' },
    { code: 'SG', name: 'Singapore', complianceRate: 92, pendingAlerts: 1, trend: 'stable' },
    { code: 'EU', name: 'European Union', complianceRate: 78, pendingAlerts: 7, trend: 'down' },
    { code: 'US', name: 'United States', complianceRate: 88, pendingAlerts: 2, trend: 'up' },
];

// Mock data
const mockComplianceTrends: ComplianceTrendData[] = [
    { month: 'Jan', complianceRate: 75, criticalAlerts: 12 },
    { month: 'Feb', complianceRate: 78, criticalAlerts: 10 },
    { month: 'Mar', complianceRate: 80, criticalAlerts: 8 },
    { month: 'Apr', complianceRate: 82, criticalAlerts: 9 },
    { month: 'May', complianceRate: 85, criticalAlerts: 7 },
    { month: 'Jun', complianceRate: 87, criticalAlerts: 5 },
];

// Mock data
const mockRiskDistribution: RiskDistribution[] = [
    { type: 'High Risk', count: 15, color: '#dc2626' },
    { type: 'Medium Risk', count: 30, color: '#d97706' },
    { type: 'Low Risk', count: 55, color: '#059669' },
];

// Mock data
const mockRegulatoryUpdates = [
    { id: 1, date: '2025-06-20', title: 'New data residency requirements for MY cloud services', category: 'Data Privacy' },
    { id: 2, date: '2025-06-10', title: 'Updates to Singapore Payment Services Act', category: 'Financial Compliance' },
    { id: 3, date: '2025-05-25', title: 'EU AI Act final provisions published', category: 'AI Regulation' },
];

export default function Compliance() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
            <Header />

            <main className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
                <h1 className="text-4xl font-extrabold text-white mb-8 text-center drop-shadow-lg">Compliance Dashboard</h1>

                {/* Jurisdiction overiew cards */}
                <section className="mb-12">
                    <h2 className="text-2xl font-semibold text-blue-300 mb-6">Jurisdiction Overview</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {mockJurisdictions.map(jur => (
                            <div key={jur.code} className="bg-slate-800 p-6 rounded-lg shadow-xl border border-slate-700 hover:shadow-blue-500/30 transform hover:scale-[1.02] transition-all duration-200 cursor-pointer">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-lg font-bold text-white">{jur.name} ({jur.code})</span>
                                    <Globe className="w-6 h-6 text-blue-400" />
                                </div>
                                <div className="space-y-2">
                                    <p className="text-sm text-gray-300">
                                        Compliance Rate: <span className="font-semibold text-white">{jur.complianceRate}%</span>
                                        <span className={`ml-2 text-xs font-medium ${jur.trend === 'up' ? 'text-green-500' : jur.trend === 'down' ? 'text-red-500' : 'text-gray-400'}`}>
                                            {jur.trend === 'up' && <TrendingUp className="inline-block w-4 h-4 mr-1" />}
                                            {jur.trend === 'down' && <TrendingDown className="inline-block w-4 h-4 mr-1" />}
                                            {jur.trend === 'stable' && <Info className="inline-block w-4 h-4 mr-1" />}
                                            {jur.trend}
                                        </span>
                                    </p>
                                    <p className="text-sm text-gray-300 flex items-center gap-1">
                                        <AlertCircle className="w-4 h-4 text-amber-400" /> Pending Alerts: <span className="font-semibold text-white">{jur.pendingAlerts}</span>
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Compliance trend chart */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <section className="lg:col-span-2 bg-slate-800 p-6 rounded-lg shadow-2xl border border-slate-700">
                        <h2 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                            <BarChart2 className="w-6 h-6" /> Compliance Trends
                        </h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={mockComplianceTrends} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                                <XAxis dataKey="month" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
                                    itemStyle={{ color: '#e2e8f0' }}
                                    labelStyle={{ color: '#cbd5e1' }}
                                />
                                <Line type="monotone" dataKey="complianceRate" stroke="#059669" name="Compliance Rate" dot={{ stroke: '#059669', strokeWidth: 2, r: 4 }} />
                                <Line type="monotone" dataKey="criticalAlerts" stroke="#dc2626" name="Critical Alerts" dot={{ stroke: '#dc2626', strokeWidth: 2, r: 4 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </section>

                    {/* Risk distribution pie chart */}
                    <section className="lg:col-span-1 bg-slate-800 p-6 rounded-lg shadow-2xl border border-slate-700">
                        <h2 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                            <PieChart className="w-6 h-6" /> Risk Distribution
                        </h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <RechartsPieChart>
                                <Pie
                                    data={mockRiskDistribution}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="count"
                                    nameKey="type"
                                >
                                    {mockRiskDistribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
                                    itemStyle={{ color: '#e2e8f0' }}
                                    labelStyle={{ color: '#cbd5e1' }}
                                />
                                <Legend
                                    wrapperStyle={{ color: '#e2e8f0' }}
                                    formatter={(value, entry) => {
                                        const dataItem = entry.payload as unknown as RiskDistribution;
                                        return (
                                        <span className="text-gray-300">
                                            {value} ({dataItem?.count ?? 0})
                                        </span>
                                        );
                                    }}
                                />
                            </RechartsPieChart>
                        </ResponsiveContainer>
                    </section>
                </div>

                {/* Recent regulatory updates */}
                <section className="mt-8 bg-slate-800 p-6 rounded-lg shadow-2xl border border-slate-700">
                    <h2 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                        <Info className="w-6 h-6" /> Recent Regulatory Updates
                    </h2>
                    <div className="divide-y divide-slate-700/50">
                        {mockRegulatoryUpdates.map(update => (
                            <div key={update.id} className="py-3 flex items-start gap-4">
                                <Calendar className="w-5 h-5 text-gray-400 flex-shrink-0 mt-1" />
                                <div>
                                    <p className="text-white font-medium">{update.title}</p>
                                    <p className="text-sm text-gray-400 mt-0.5">{update.date} - <span className="font-semibold">{update.category}</span></p>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Compliance requirements checklist */}
                <section className="mt-8 bg-slate-800 p-6 rounded-lg shadow-2xl border border-slate-700">
                    <h2 className="text-xl font-semibold text-blue-300 mb-4 flex items-center gap-2">
                        <CheckSquare className="w-6 h-6" /> Compliance Requirements
                    </h2>

                    <div className="space-y-6">
                        {Object.entries(complianceChecklist).map(([categoryKey, value]) => (
                        <div
                            key={categoryKey}
                            className="bg-slate-900/40 p-5 rounded-xl border border-slate-700 hover:shadow-md transition-shadow"
                        >
                            <h3 className="text-lg font-bold text-white mb-4 capitalize tracking-wide">
                            {categoryKey.replace(/_/g, " ")}
                            </h3>
                            <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3">
                            {value.requirements.map((req, idx) => (
                                <label
                                key={idx}
                                htmlFor={`${categoryKey}-${req}`}
                                className="flex items-center gap-3 bg-slate-800/40 hover:bg-slate-700/40 px-4 py-2 rounded-md cursor-pointer transition-colors"
                                >
                                <input
                                    type="checkbox"
                                    id={`${categoryKey}-${req}`}
                                    className="h-4 w-4 text-green-500 border-gray-500 rounded focus:ring-0 bg-slate-900"
                                />
                                <span className="text-sm text-gray-300">
                                    {req.replace(/_/g, " ")}
                                </span>
                                </label>
                            ))}
                            </div>
                        </div>
                        ))}
                    </div>
                </section>
            </main>
        </div>
    );
}
