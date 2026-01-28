import { apiService } from './api';

class RiskService {
  async getAllRisks() {
    try {
      const risks = await apiService.get('/api/risks');
      return risks;
    } catch (error) {
      console.error('Error fetching risks:', error);
      throw error;
    }
  }

  async checkRisks() {
    try {
      const result = await apiService.get('/api/risks/check');
      return result;
    } catch (error) {
      console.error('Error checking risks:', error);
      throw error;
    }
  }
}

export const riskService = new RiskService();