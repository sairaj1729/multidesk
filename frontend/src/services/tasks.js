import { apiService } from './api';

class TasksService {
  constructor() {
    this.basePath = '/api/tasks';
  }

  async getTasks(filters = {}, page = 1, size = 50) {
    try {
      // Build query parameters
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('size', size);
      
      // Add filters if provided
      if (filters.search) params.append('search', filters.search);
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.project) params.append('project', filters.project);
      if (filters.assignee) params.append('assignee', filters.assignee);
      
      const queryString = params.toString();
      const url = queryString ? `${this.basePath}/?${queryString}` : `${this.basePath}/`;
      
      const response = await apiService.get(url);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      return { success: false, error: error.message };
    }
  }

  async getTaskById(taskId) {
    try {
      const response = await apiService.get(`${this.basePath}/${taskId}`);
      return { success: true, data: response };
    } catch (error) {
      console.error(`Failed to fetch task ${taskId}:`, error);
      return { success: false, error: error.message };
    }
  }
}

export const tasksService = new TasksService();