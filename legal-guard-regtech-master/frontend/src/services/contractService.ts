import api from './api'

// Analyze Single Contract with Text
export const analyzeContract = (data: { text: string; jurisdiction: string }) =>
    api.post('/api/v1/contracts/analyze', data, {
        headers: {
            'Content-Type': 'application/json',
        },
    });

// Analyze Contract File
export const analyzeContractFile = (formData: FormData) =>
    api.post('/api/v1/contracts/analyze/file', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

// Analyze Bulk Contracts
export const analyzeBulkContract = (formData: FormData) =>
    api.post('/api/v1/contracts/analyze/bulk', formData);

// Calculate Risk Score
export const calculateRiskScore = (analysisData: any) =>
    api.post('/api/v1/contracts/risk-score', analysisData, {
        headers: {
            'Content-Type': 'application/json',
        },
    });

// Extract Text from Contract File
export const extractText = (formData: FormData) =>
    api.post('/api/v1/contracts/extract-text', formData);

// Get Supported Jurisdictions
export const getSupportedJurisdictions = () =>
    api.get('/api/v1/contracts/supported-jurisdictions');

// Health Check
export const healthCheck = () =>
    api.get('/api/v1/contracts/health');