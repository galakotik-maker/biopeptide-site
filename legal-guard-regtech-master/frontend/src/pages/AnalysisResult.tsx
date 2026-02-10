import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AlertTriangle, CheckCircle, XCircle, Shield, BookOpen, ArrowLeft, Download, FileText } from 'lucide-react';
import Header from '../components/layout/Header';
import RiskScoreDisplay from '../components/RiskScoreDisplay';
import { calculateRiskScore } from '../services/contractService';
import { downloadAnalysisReport } from '../services/pdfService';

interface FlaggedClause {
    clause_text: string;
    issue: string;
    severity: 'low' | 'medium' | 'high';
}

interface ComplianceIssue {
    law: string;
    missing_requirements: string[];
    recommendations: string[];
}

interface AnalysisResult {
    summary: string;
    flagged_clauses: FlaggedClause[];
    compliance_issues: ComplianceIssue[];
    jurisdiction: string;
}

interface ComplianceRiskScore {
    overall_score: number;
    financial_risk_estimate: number;
    violation_categories: string[];
    jurisdiction_risks: Record<string, number>;
}

export default function AnalysisResults() {
    const { analysisId } = useParams<{ analysisId: string }>();
    const navigate = useNavigate();
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [riskScore, setRiskScore] = useState<ComplianceRiskScore | null>(null);
    const [loading, setLoading] = useState(true);
    const [loadingRiskScore, setLoadingRiskScore] = useState(false);
    const [downloadingPDF, setDownloadingPDF] = useState(false);

    useEffect(() => {
        if (!analysisId) {
            navigate('/analyze');
            return;
        }

        const storedResult = localStorage.getItem(`analysis-${analysisId}`);
        if (storedResult) {
            try {
                const parsedResult = JSON.parse(storedResult);
                setResult(parsedResult);
                
                // Fetch risk score
                fetchRiskScore(parsedResult);
            } catch (error) {
                console.error('Error parsing stored result:', error);
                navigate('/analyze');
            }
        } else {
            navigate('/analyze');
        }
        setLoading(false);
    }, [analysisId, navigate]);

    const fetchRiskScore = async (analysisResult: AnalysisResult) => {
        try {
            setLoadingRiskScore(true);
            const response = await calculateRiskScore(analysisResult);
            setRiskScore(response.data);
        } catch (error) {
            console.error('Error fetching risk score:', error);
            // Continue without risk score if it fails
        } finally {
            setLoadingRiskScore(false);
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'high':
                return 'bg-red-700/20 text-red-300 border-red-500';
            case 'medium':
                return 'bg-amber-700/20 text-amber-200 border-amber-500';
            case 'low':
                return 'bg-green-700/20 text-green-200 border-green-500';
            default:
                return 'bg-gray-700/20 text-gray-200 border-gray-500';
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'high':
                return <XCircle className="w-5 h-5 text-red-400" />;
            case 'medium':
                return <AlertTriangle className="w-5 h-5 text-amber-400" />;
            case 'low':
                return <CheckCircle className="w-5 h-5 text-green-400" />;
            default:
                return <AlertTriangle className="w-5 h-5 text-gray-400" />;
        }
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

    const handleDownloadReport = async () => {
        if (!result) return;
        
        try {
            setDownloadingPDF(true);
            
            // Generate a nice filename
            const jurisdictionCode = result.jurisdiction;
            const date = new Date().toISOString().split('T')[0];
            const time = new Date().toTimeString().split(' ')[0].replace(/:/g, '-');
            const filename = `LegalGuard-Analysis-${jurisdictionCode}-${date}-${time}.pdf`;
            
            // Generate and download the PDF report
            downloadAnalysisReport(result, riskScore, filename);
            
        } catch (error) {
            console.error('Error generating PDF report:', error);
            // You could add a toast notification here for better UX
        } finally {
            setDownloadingPDF(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
                <Header />
                <div className="max-w-5xl mx-auto py-16 px-4 text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
                    <p className="mt-4 text-gray-300">Loading analysis results...</p>
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
                <Header />
                <div className="max-w-5xl mx-auto py-16 px-4 text-center">
                    <XCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <h1 className="text-2xl font-bold mb-4">Analysis Not Found</h1>
                    <p className="text-gray-300 mb-6">The requested analysis could not be found.</p>
                    <Link to="/analyze" className="bg-blue-700 hover:bg-blue-800 px-6 py-3 rounded-md text-white font-medium transition">
                        Back to Analysis
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
            <Header />

            <main className="max-w-7xl mx-auto py-8 px-4">
                {/* Header Section */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/analyze')}
                            className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                            Back to Analysis
                        </button>
                        <div className="h-6 w-px bg-slate-600"></div>
                        <h1 className="text-2xl font-bold">Contract Analysis Results</h1>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-400">Jurisdiction:</span>
                        <span className="px-3 py-1 bg-blue-700/30 text-blue-200 rounded-full text-sm font-medium border border-blue-500/20">
                            {getJurisdictionName(result.jurisdiction)}
                        </span>
                    </div>
                </div>

                {/* Summary Section */}
                <div className="mb-8">
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-xl">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-blue-700/20 rounded-lg">
                                <FileText className="w-6 h-6 text-blue-400" />
                            </div>
                            <div className="flex-1">
                                <h2 className="text-xl font-semibold text-blue-300 mb-3">Analysis Summary</h2>
                                <p className="text-gray-300 leading-relaxed">{result.summary}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Risk Score Section */}
                {riskScore && (
                    <div className="mb-8">
                        <RiskScoreDisplay riskScore={riskScore} jurisdiction={result.jurisdiction} />
                    </div>
                )}

                {loadingRiskScore && (
                    <div className="mb-8">
                        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-xl">
                            <div className="flex items-center gap-4">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                                <p className="text-gray-300">Calculating compliance risk score...</p>
                            </div>
                        </div>
                    </div>
                )}

                <div className="grid lg:grid-cols-2 gap-8">
                    {/* Flagged Clauses */}
                    <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-xl">
                        <div className="p-6 border-b border-slate-700">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-6 h-6 text-amber-400" />
                                <h2 className="text-xl font-semibold text-amber-300">
                                    Flagged Clauses ({result.flagged_clauses.length})
                                </h2>
                            </div>
                        </div>
                        <div className="p-6">
                            {result.flagged_clauses.length > 0 ? (
                                <div className="space-y-4">
                                    {result.flagged_clauses.map((clause, index) => (
                                        <div key={index} className="border border-slate-600 rounded-lg p-4 hover:bg-slate-700/30 transition-colors">
                                            <div className="flex items-start justify-between mb-3">
                                                <div className="flex items-center gap-2">
                                                    {getSeverityIcon(clause.severity)}
                                                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(clause.severity)}`}>
                                                        {clause.severity.toUpperCase()}
                                                    </span>
                                                </div>
                                            </div>
                                            <p className="text-red-300 font-medium mb-2">{clause.issue}</p>
                                            <div className="bg-slate-900/50 p-3 rounded border border-slate-600">
                                                <p className="text-sm text-gray-300 font-mono leading-relaxed">
                                                    {clause.clause_text.length > 200 
                                                        ? `${clause.clause_text.substring(0, 200)}...` 
                                                        : clause.clause_text
                                                    }
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
                                    <p className="text-gray-300">No flagged clauses found</p>
                                    <p className="text-sm text-gray-400">All clauses appear to be compliant</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Compliance Issues */}
                    <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-xl">
                        <div className="p-6 border-b border-slate-700">
                            <div className="flex items-center gap-3">
                                <Shield className="w-6 h-6 text-purple-400" />
                                <h2 className="text-xl font-semibold text-purple-300">
                                    Compliance Issues ({result.compliance_issues.length})
                                </h2>
                            </div>
                        </div>
                        <div className="p-6">
                            {result.compliance_issues.length > 0 ? (
                                <div className="space-y-6">
                                    {result.compliance_issues.map((issue, index) => (
                                        <div key={index} className="border border-slate-600 rounded-lg p-4">
                                            <div className="flex items-center gap-3 mb-4">
                                                <BookOpen className="w-5 h-5 text-purple-400" />
                                                <h3 className="text-lg font-semibold text-purple-300">{issue.law}</h3>
                                            </div>
                                            
                                            {/* Missing Requirements */}
                                            <div className="mb-4">
                                                <h4 className="text-sm font-medium text-red-300 mb-2">Missing Requirements:</h4>
                                                <ul className="space-y-1">
                                                    {issue.missing_requirements.map((req, reqIndex) => (
                                                        <li key={reqIndex} className="flex items-start gap-2 text-sm text-gray-300">
                                                            <XCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                                                            <span>{req}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>

                                            {/* Recommendations */}
                                            <div>
                                                <h4 className="text-sm font-medium text-green-300 mb-2">Recommendations:</h4>
                                                <ul className="space-y-1">
                                                    {issue.recommendations.map((rec, recIndex) => (
                                                        <li key={recIndex} className="flex items-start gap-2 text-sm text-gray-300">
                                                            <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                                                            <span>{rec}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <Shield className="w-12 h-12 text-green-400 mx-auto mb-3" />
                                    <p className="text-gray-300">No compliance issues found</p>
                                    <p className="text-sm text-gray-400">Contract meets all regulatory requirements</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                    <button 
                        onClick={handleDownloadReport}
                        disabled={downloadingPDF}
                        className="flex items-center gap-2 bg-blue-700 hover:bg-blue-800 disabled:bg-blue-900 disabled:cursor-not-allowed px-6 py-3 rounded-md text-white font-medium transition"
                    >
                        {downloadingPDF ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                Generating PDF...
                            </>
                        ) : (
                            <>
                                <Download className="w-5 h-5" />
                                Download Report
                            </>
                        )}
                    </button>
                    <Link
                        to="/analyze"
                        className="flex items-center gap-2 border border-slate-600 hover:bg-slate-700 px-6 py-3 rounded-md text-white font-medium transition text-center justify-center"
                    >
                        Analyze Another Contract
                    </Link>
                </div>
            </main>
        </div>
    );
}
