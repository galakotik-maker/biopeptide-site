import api from './api';

export interface DocumentSummaryRequest {
    text: string;
    summary_type?: 'plain_language' | 'executive' | 'risks';
}

export interface DocumentSummaryResponse {
    summary: string;
    key_points: string[];
    risk_level: string;
    word_count_reduction: string;
}

export interface ClauseExplanationRequest {
    clause_text: string;
}

export interface ClauseExplanationResponse {
    plain_english: string;
    potential_risks: string[];
    recommendations: string[];
}

export interface HealthCheckResponse {
    status: string;
    ai_service?: string;
    error?: string;
}

class AIInsightsService {
    private readonly baseUrl = '/ai';

    async summarizeDocument(request: DocumentSummaryRequest): Promise<DocumentSummaryResponse> {
        try {
            const response = await api.post(`${this.baseUrl}/summarize`, {
                text: request.text,
                summary_type: request.summary_type || 'plain_language'
            });
            return response.data;
        } catch (error) {
            console.error('Error summarizing document:', error);
            throw error;
        }
    }

    async explainClause(request: ClauseExplanationRequest): Promise<ClauseExplanationResponse> {
        try {
            const response = await api.post(`${this.baseUrl}/explain-clause`, request);
            return response.data;
        } catch (error) {
            console.error('Error explaining clause:', error);
            throw error;
        }
    }

    async checkHealth(): Promise<HealthCheckResponse> {
        try {
            const response = await api.get(`${this.baseUrl}/health`);
            return response.data;
        } catch (error) {
            console.error('Error checking AI service health:', error);
            throw error;
        }
    }
}

export const aiInsightsService = new AIInsightsService();
