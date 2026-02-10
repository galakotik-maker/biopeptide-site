import { useCallback, useEffect, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, CheckCircle, XCircle, Info, File, FileText, Edit3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import { getJurisdictions } from '../services/regulatoryService';
import { analyzeContractFile, analyzeContract } from '../services/contractService';

type FileWithMeta = File & {
    status: 'pending' | 'uploaded' | 'failed';
    analysisId?: string;
};

type AnalysisMode = 'file' | 'text';

export default function Analyze() {
    const [mode, setMode] = useState<AnalysisMode>('file');
    const [file, setFile] = useState<FileWithMeta | null>(null);
    const [contractText, setContractText] = useState('');
    const [jurisdiction, setJurisdiction] = useState('');
    const [jurisdictions, setJurisdictions] = useState<{ code: string; name: string }[]>([]);
    const [status, setStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'complete' | 'error'>('idle');
    const [progress, setProgress] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchJurisdictions = async () => {
            try {
                console.log("Starting to fetch jurisdictions...");
                const response = await getJurisdictions();
                console.log("Full response:", response);
                console.log("Response data:", response?.data);
                console.log("Response status:", response?.status);

                const codes: string[] = response?.data?.jurisdictions ?? [];
                console.log("Extracted codes:", codes);

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

                console.log("Formatted jurisdictions:", formatted);
                setJurisdictions(formatted);
            } catch (error: any) {
                console.error('Failed to fetch jurisdictions:', error);
                console.error('Error details:', error.response?.data);
                console.error('Error status:', error.response?.status);
            }
        };

        fetchJurisdictions();
    }, []);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            const uploaded = Object.assign(acceptedFiles[0], { status: 'pending' }) as FileWithMeta;
            setFile(uploaded);
            setStatus('idle');
            setProgress(0);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        multiple: false,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'text/plain': ['.txt'],
        },
    });

    const removeFile = () => {
        setFile(null);
    };

    const isFormValid = () => {
        if (mode === 'file') {
            return file && jurisdiction;
        } else {
            return contractText.trim() && jurisdiction;
        }
    };

    const handleAnalyze = async () => {
        if (!isFormValid()) {
            alert('Please fill all required fields.');
            return;
        }

        setStatus('uploading');
        setProgress(10);

        try {
            // Simulate upload progress
            await new Promise((res) => setTimeout(res, 500));
            setProgress(30);

            let response;
            
            if (mode === 'file' && file) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('jurisdiction', jurisdiction);
                response = await analyzeContractFile(formData);
                file.status = 'uploaded';
            } else {
                const data = {
                    text: contractText,
                    jurisdiction: jurisdiction
                };
                response = await analyzeContract(data);
            }

            setStatus('analyzing');
            setProgress(50);

            await new Promise((res) => setTimeout(res, 1000));
            setProgress(80);

            const result = response.data;
            console.log('Analysis result:', result);

            // Generate a unique analysis ID
            const analysisId = `ANALYSIS-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
            
            if (file) {
                file.analysisId = analysisId;
            }

            // Store the result in localStorage for the results page
            localStorage.setItem(`analysis-${analysisId}`, JSON.stringify(result));

            setProgress(100);
            setStatus('complete');

            // Navigate to results page after a brief delay
            setTimeout(() => {
                navigate(`/analysis/${analysisId}`);
            }, 1000);
        } catch (err) {
            console.error('Error during analysis:', err);
            setStatus('error');
            setProgress(0);
            if (file) {
                file.status = 'failed';
            }
            alert('Failed to analyze contract. Please try again.');
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
            <Header />

            <main className="max-w-5xl mx-auto py-16 px-4">
                {/* Hero section */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                        Contract Analysis
                    </h1>
                    <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                        Upload your contract file or paste contract text to get AI-powered compliance analysis
                    </p>
                </div>

                {/* Mode Selection */}
                <div className="mb-8">
                    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                        <h2 className="text-xl font-semibold text-blue-300 mb-4">Analysis Method</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => setMode('file')}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                    mode === 'file'
                                        ? 'border-blue-500 bg-blue-900/20 text-blue-300'
                                        : 'border-slate-600 hover:border-slate-500 text-gray-300'
                                }`}
                            >
                                <div className="flex items-center gap-3 mb-2">
                                    <Upload className="w-6 h-6" />
                                    <span className="font-semibold">Upload File</span>
                                </div>
                                <p className="text-sm opacity-80">
                                    Upload PDF, DOCX, or TXT files
                                </p>
                            </button>
                            <button
                                onClick={() => setMode('text')}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                    mode === 'text'
                                        ? 'border-blue-500 bg-blue-900/20 text-blue-300'
                                        : 'border-slate-600 hover:border-slate-500 text-gray-300'
                                }`}
                            >
                                <div className="flex items-center gap-3 mb-2">
                                    <Edit3 className="w-6 h-6" />
                                    <span className="font-semibold">Paste Text</span>
                                </div>
                                <p className="text-sm opacity-80">
                                    Copy and paste contract text
                                </p>
                            </button>
                        </div>
                    </div>
                </div>

                {/* File Upload Section */}
                {mode === 'file' && (
                    <div className="mb-8">
                        <div
                            {...getRootProps()}
                            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer ${
                                isDragActive
                                    ? 'border-blue-500 bg-blue-900/10 scale-105'
                                    : 'border-slate-600 hover:border-blue-500 hover:bg-slate-700/20'
                            }`}
                        >
                            <input {...getInputProps()} />
                            <Upload className="w-16 h-16 mx-auto text-blue-400 mb-4" />
                            <h3 className="text-xl font-semibold mb-2">
                                {isDragActive ? 'Drop your file here' : 'Upload Contract Document'}
                            </h3>
                            <p className="text-gray-400 mb-2">
                                Drag & drop a file here or click to browse
                            </p>
                            <p className="text-sm text-gray-500">
                                Supported formats: PDF, DOCX, TXT (max 5MB)
                            </p>
                        </div>

                        {/* Uploaded file display */}
                        {file && (
                            <div className="mt-6">
                                <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                                    <h3 className="text-lg font-semibold text-blue-300 mb-4">Uploaded File</h3>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-4">
                                            <div className="p-3 bg-blue-700/20 rounded-lg">
                                                <File className="w-6 h-6 text-blue-400" />
                                            </div>
                                            <div>
                                                <p className="font-medium text-white">{file.name}</p>
                                                <p className="text-sm text-gray-400">
                                                    {(file.size / 1024).toFixed(2)} KB
                                                </p>
                                            </div>
                                            <div className="ml-4">
                                                {file.status === 'uploaded' && (
                                                    <CheckCircle className="w-6 h-6 text-green-400" />
                                                )}
                                                {file.status === 'failed' && (
                                                    <XCircle className="w-6 h-6 text-red-400" />
                                                )}
                                            </div>
                                        </div>
                                        <button
                                            onClick={removeFile}
                                            className="p-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition-colors"
                                        >
                                            <XCircle className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Text Input Section */}
                {mode === 'text' && (
                    <div className="mb-8">
                        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                            <div className="flex items-center gap-3 mb-4">
                                <FileText className="w-6 h-6 text-blue-400" />
                                <h3 className="text-lg font-semibold text-blue-300">Contract Text</h3>
                            </div>
                            <textarea
                                value={contractText}
                                onChange={(e) => setContractText(e.target.value)}
                                placeholder="Paste your contract text here..."
                                className="w-full h-64 p-4 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-vertical font-mono text-sm leading-relaxed"
                            />
                            <p className="text-xs text-gray-400 mt-2">
                                {contractText.length} characters • Supports all text-based contracts
                            </p>
                        </div>
                    </div>
                )}

                {/* Configuration section */}
                <div className="mb-8">
                    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                        <h2 className="text-xl font-semibold text-blue-300 mb-6">Analysis Configuration</h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-3">
                                Jurisdiction <span className="text-red-400">*</span>
                            </label>
                            {/* Debug info */}
                            <select
                                value={jurisdiction}
                                onChange={(e) => setJurisdiction(e.target.value)}
                                className="w-full p-4 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                            >
                                <option value="">Select jurisdiction for compliance analysis</option>
                                {jurisdictions.map((j) => (
                                    <option key={j.code} value={j.code}>
                                        {j.name}
                                    </option>
                                ))}
                            </select>
                            <p className="text-xs text-gray-400 mt-2">
                                Choose the jurisdiction to analyze compliance against specific regulations
                            </p>
                        </div>
                    </div>
                </div>

                {/* Status and Progress */}
                {status !== 'idle' && (
                    <div className="mb-8">
                        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                            <div className="flex items-center gap-4 mb-4">
                                {status === 'uploading' && (
                                    <Upload className="w-6 h-6 animate-bounce text-blue-400" />
                                )}
                                {status === 'analyzing' && (
                                    <Info className="w-6 h-6 animate-pulse text-yellow-400" />
                                )}
                                {status === 'complete' && (
                                    <CheckCircle className="w-6 h-6 text-green-400" />
                                )}
                                {status === 'error' && (
                                    <XCircle className="w-6 h-6 text-red-400" />
                                )}
                                <div>
                                    <h3 className="font-semibold capitalize text-white">{status}</h3>
                                    <p className="text-sm text-gray-400">
                                        {status === 'uploading' && (mode === 'file' ? 'Uploading your document...' : 'Processing your text...')}
                                        {status === 'analyzing' && 'Analyzing contract for compliance issues...'}
                                        {status === 'complete' && 'Analysis completed successfully!'}
                                        {status === 'error' && 'An error occurred during analysis'}
                                    </p>
                                </div>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-3">
                                <div
                                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                            <p className="text-right text-sm text-gray-400 mt-2">{progress}%</p>
                        </div>
                    </div>
                )}

                {/* Action button */}
                <div className="text-center">
                    <button
                        onClick={handleAnalyze}
                        disabled={!isFormValid() || status === 'uploading' || status === 'analyzing'}
                        className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-xl text-white font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1 disabled:transform-none"
                    >
                        {status === 'uploading'
                            ? (mode === 'file' ? 'Uploading Document...' : 'Processing Text...')
                            : status === 'analyzing'
                            ? 'Analyzing Contract...'
                            : 'Start Analysis'}
                    </button>
                    <p className="text-sm text-gray-400 mt-3">
                        Analysis typically takes 30-60 seconds depending on content size
                    </p>
                </div>
            </main>
        </div>
    );
}
