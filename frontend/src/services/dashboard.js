import { apiService } from './api';

class DashboardService {
  constructor() {
    this.basePath = '/api/dashboard';
  }

  async getDashboardData() {
    try {
      const response = await apiService.get(`${this.basePath}/`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      return { success: false, error: error.message };
    }
  }

  async getDashboardStats() {
    try {
      const response = await apiService.get(`${this.basePath}/stats`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      return { success: false, error: error.message };
    }
  }

  async getEisenhowerMatrix() {
    try {
      const response = await apiService.get(`${this.basePath}/eisenhower`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch Eisenhower matrix:', error);
      return { success: false, error: error.message };
    }
  }

  async getAnalyticsData() {
    try {
      const response = await apiService.get(`${this.basePath}/analytics`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
      return { success: false, error: error.message };
    }
  }
}

export const dashboardService = new DashboardService();