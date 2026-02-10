import { useEffect, useState } from 'react';
import { AlertTriangle, DollarSign, Shield, TrendingUp, TrendingDown, Gauge } from 'lucide-react';

interface ComplianceRiskScore {
    overall_score: number;
    financial_risk_estimate: number;
    violation_categories: string[];
    jurisdiction_risks: Record<string, number>;
}

interface RiskScoreDisplayProps {
    riskScore: ComplianceRiskScore;
    jurisdiction: string;
}

export default function RiskScoreDisplay({ riskScore, jurisdiction }: RiskScoreDisplayProps) {
    const [animatedScore, setAnimatedScore] = useState(0);

    useEffect(() => {
        // Animate the score counter
        const duration = 2000; // 2 seconds
        const steps = 60;
        const increment = riskScore.overall_score / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= riskScore.overall_score) {
                setAnimatedScore(riskScore.overall_score);
                clearInterval(timer);
            } else {
                setAnimatedScore(Math.floor(current));
            }
        }, duration / steps);

        return () => clearInterval(timer);
    }, [riskScore.overall_score]);

    const getScoreColor = (score: number) => {
        if (score >= 90) return 'text-green-400';
        if (score >= 70) return 'text-yellow-400';
        if (score >= 50) return 'text-orange-400';
        return 'text-red-400';
    };

    const getRiskLevel = (score: number) => {
        if (score >= 90) return { level: 'Low Risk', icon: Shield, color: 'text-green-400' };
        if (score >= 70) return { level: 'Medium Risk', icon: AlertTriangle, color: 'text-yellow-400' };
        if (score >= 50) return { level: 'High Risk', icon: TrendingDown, color: 'text-orange-400' };
        return { level: 'Critical Risk', icon: TrendingDown, color: 'text-red-400' };
    };

    const formatCurrency = (amount: number) => {
        if (amount >= 1000000) {
            return `$${(amount / 1000000).toFixed(1)}M`;
        } else if (amount >= 1000) {
            return `$${(amount / 1000).toFixed(0)}K`;
        }
        return `$${amount.toLocaleString()}`;
    };

    const getJurisdictionName = (code: string) => {
        const jurisdictionNames: Record<string, string> = {
            MY: 'Malaysia',
            SG: 'Singapore',
            EU: 'European Union',
            US: 'United States'
        };
        return jurisdictionNames[code] || code;
    };

    const riskInfo = getRiskLevel(riskScore.overall_score);
    const RiskIcon = riskInfo.icon;

    return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-xl">
            <div className="p-6 border-b border-slate-700">
                <div className="flex items-center gap-3">
                    <Gauge className="w-6 h-6 text-blue-400" />
                    <h2 className="text-xl font-semibold text-blue-300">Compliance Risk Assessment</h2>
                </div>
            </div>
            
            <div className="p-6">
                {/* Overall Score Circle */}
                <div className="flex flex-col lg:flex-row gap-8 mb-8">
                    <div className="flex-1">
                        <div className="relative w-48 h-48 mx-auto mb-6">
                            {/* Background circle */}
                            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="40"
                                    stroke="currentColor"
                                    strokeWidth="8"
                                    fill="none"
                                    className="text-slate-600"
                                />
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="40"
                                    stroke="url(#gradient)"
                                    strokeWidth="8"
                                    fill="none"
                                    strokeLinecap="round"
                                    strokeDasharray={`${(animatedScore / 100) * 251.2} 251.2`}
                                    className="transition-all duration-1000 ease-out"
                                />
                                <defs>
                                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        {riskScore.overall_score >= 90 ? (
                                            <>
                                                <stop offset="0%" stopColor="#10b981" />
                                                <stop offset="100%" stopColor="#059669" />
                                            </>
                                        ) : riskScore.overall_score >= 70 ? (
                                            <>
                                                <stop offset="0%" stopColor="#f59e0b" />
                                                <stop offset="100%" stopColor="#d97706" />
                                            </>
                                        ) : riskScore.overall_score >= 50 ? (
                                            <>
                                                <stop offset="0%" stopColor="#f97316" />
                                                <stop offset="100%" stopColor="#ea580c" />
                                            </>
                                        ) : (
                                            <>
                                                <stop offset="0%" stopColor="#ef4444" />
                                                <stop offset="100%" stopColor="#dc2626" />
                                            </>
                                        )}
                                    </linearGradient>
                                </defs>
                            </svg>
                            
                            {/* Score text */}
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className={`text-4xl font-bold ${getScoreColor(riskScore.overall_score)}`}>
                                    {animatedScore}
                                </span>
                                <span className="text-gray-400 text-sm">/ 100</span>
                            </div>
                        </div>
                        
                        <div className="text-center">
                            <div className="flex items-center justify-center gap-2 mb-2">
                                <RiskIcon className={`w-6 h-6 ${riskInfo.color}`} />
                                <span className={`text-lg font-semibold ${riskInfo.color}`}>
                                    {riskInfo.level}
                                </span>
                            </div>
                            <p className="text-sm text-gray-400">
                                Overall Compliance Score
                            </p>
                        </div>
                    </div>

                    {/* Risk Metrics */}
                    <div className="flex-1 space-y-4">
                        {/* Financial Risk */}
                        <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-red-700/20 rounded-lg">
                                    <DollarSign className="w-5 h-5 text-red-400" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-white">Financial Risk Estimate</h3>
                                    <p className="text-2xl font-bold text-red-400">
                                        {formatCurrency(riskScore.financial_risk_estimate)}
                                    </p>
                                </div>
                            </div>
                            <p className="text-sm text-gray-400">
                                Potential financial exposure from compliance violations
                            </p>
                        </div>

                        {/* Violation Categories */}
                        <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="p-2 bg-amber-700/20 rounded-lg">
                                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-white">Violation Categories</h3>
                                    <p className="text-lg font-bold text-amber-400">
                                        {riskScore.violation_categories.length}
                                    </p>
                                </div>
                            </div>
                            <div className="space-y-1">
                                {riskScore.violation_categories.map((category, index) => (
                                    <div key={index} className="text-sm text-gray-300 bg-slate-600/50 px-2 py-1 rounded">
                                        {category}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Jurisdiction Risks */}
                        <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="p-2 bg-purple-700/20 rounded-lg">
                                    <TrendingUp className="w-5 h-5 text-purple-400" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-white">Jurisdiction Risk</h3>
                                    <p className="text-lg font-bold text-purple-400">
                                        {getJurisdictionName(jurisdiction)}
                                    </p>
                                </div>
                            </div>
                            <div className="space-y-2">
                                {Object.entries(riskScore.jurisdiction_risks).map(([jur, risk]) => (
                                    <div key={jur} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-300">
                                            {getJurisdictionName(jur)}
                                        </span>
                                        <span className="text-sm font-semibold text-purple-300">
                                            Risk: {risk}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Risk Score Interpretation */}
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                    <h4 className="font-semibold text-white mb-2">Risk Score Interpretation</h4>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                        <div className="text-center">
                            <div className="w-4 h-4 bg-green-500 rounded mx-auto mb-1"></div>
                            <div className="font-medium text-green-400">90-100</div>
                            <div className="text-gray-400">Low Risk</div>
                        </div>
                        <div className="text-center">
                            <div className="w-4 h-4 bg-yellow-500 rounded mx-auto mb-1"></div>
                            <div className="font-medium text-yellow-400">70-89</div>
                            <div className="text-gray-400">Medium Risk</div>
                        </div>
                        <div className="text-center">
                            <div className="w-4 h-4 bg-orange-500 rounded mx-auto mb-1"></div>
                            <div className="font-medium text-orange-400">50-69</div>
                            <div className="text-gray-400">High Risk</div>
                        </div>
                        <div className="text-center">
                            <div className="w-4 h-4 bg-red-500 rounded mx-auto mb-1"></div>
                            <div className="font-medium text-red-400">0-49</div>
                            <div className="text-gray-400">Critical Risk</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
