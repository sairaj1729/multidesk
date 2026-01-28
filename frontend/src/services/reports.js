import { apiService } from './api';

class ReportsService {
  constructor() {
    this.basePath = '/api/reports';
  }

  async getReports(filters = {}, page = 1, size = 50) {
    try {
      // Build query parameters
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('size', size);
      
      // Add filters if provided
      if (filters.report_type) params.append('report_type', filters.report_type);
      
      const queryString = params.toString();
      const url = queryString ? `${this.basePath}/?${queryString}` : `${this.basePath}/`;
      
      const response = await apiService.get(url);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch reports:', error);
      return { success: false, error: error.message };
    }
  }

  async getReportById(reportId) {
    try {
      const response = await apiService.get(`${this.basePath}/${reportId}`);
      return { success: true, data: response };
    } catch (error) {
      console.error(`Failed to fetch report ${reportId}:`, error);
      return { success: false, error: error.message };
    }
  }

  async generateReport(reportData) {
    try {
      const response = await apiService.post(`${this.basePath}/generate`, reportData);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to generate report:', error);
      return { success: false, error: error.message };
    }
  }

  async deleteReport(reportId) {
    try {
      const response = await apiService.delete(`${this.basePath}/${reportId}`);
      return { success: true, data: response };
    } catch (error) {
      console.error(`Failed to delete report ${reportId}:`, error);
      return { success: false, error: error.message };
    }
  }

  async exportReport(reportId, exportData) {
    try {
      const response = await apiService.post(`${this.basePath}/${reportId}/export`, exportData);
      return { success: true, data: response };
    } catch (error) {
      console.error(`Failed to export report ${reportId}:`, error);
      return { success: false, error: error.message };
    }
  }

  async getReportableProjects() {
    try {
      const response = await apiService.get(`${this.basePath}/projects`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch reportable projects:', error);
      return { success: false, error: error.message };
    }
  }

  async getReportableUsers() {
    try {
      const response = await apiService.get(`${this.basePath}/users`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch reportable users:', error);
      return { success: false, error: error.message };
    }
  }
}

export const reportsService = new ReportsService();