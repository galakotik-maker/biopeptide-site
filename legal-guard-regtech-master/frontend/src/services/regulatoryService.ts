import api from './api';

export const getAllRegulations = () => {
    return api.get('/regulations');
};

export const getRegulationDetail = (lawId: string) => {
    return api.get(`/regulations/${lawId}`);
};

export const searchRegulations = (payload: {
    search_term?: string;
    jurisdiction?: string;
    regulation_type?: string;
    page?: number;
}) => {
    return api.post('/regulations/search', payload);
};

export const getJurisdictions = () =>
    api.get('/regulations/jurisdictions/list')
