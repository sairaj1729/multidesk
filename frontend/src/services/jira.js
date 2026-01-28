import { apiService } from './api';

class JiraService {
  constructor() {
    this.basePath = '/api/jira';
  }

  async connectJira(credentials) {
    try {
      const response = await apiService.post(`${this.basePath}/connect`, credentials);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to connect Jira:', error);
      return { success: false, error: error.message };
    }
  }

  async validateConnection() {
    try {
      const response = await apiService.post(`${this.basePath}/validate`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to validate Jira connection:', error);
      return { success: false, error: error.message };
    }
  }

  async syncJiraData() {
    try {
      const response = await apiService.post(`${this.basePath}/sync`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to sync Jira data:', error);
      return { success: false, error: error.message };
    }
  }

  async getConnectionStatus() {
    try {
      const response = await apiService.get(`${this.basePath}/connection-status`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to get Jira connection status:', error);
      return { success: false, error: error.message };
    }
  }

  // New methods matching the updated API
  async checkJiraConnection() {
    try {
      const response = await apiService.get(`${this.basePath}/connect/check`);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to check Jira connection:', error);
      return { success: false, error: error.message };
    }
  }
}

export const jiraService = new JiraService();