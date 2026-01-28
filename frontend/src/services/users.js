import { apiService } from './api';

class UsersService {
  constructor() {
    this.basePath = '/api/users';
  }

  async getUsers(filters = {}, page = 1, size = 50) {
    try {
      // Build query parameters
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('size', size);
      
      // Add filters if provided
      if (filters.search) params.append('search', filters.search);
      if (filters.role) params.append('role', filters.role);
      if (filters.status) params.append('status', filters.status);
      
      const queryString = params.toString();
      const url = queryString ? `${this.basePath}/?${queryString}` : `${this.basePath}/`;
      
      const response = await apiService.get(url);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch users:', error);
      return { success: false, error: error.message };
    }
  }

  async getUserById(userId) {
    try {
      const response = await apiService.get(`${this.basePath}/${userId}`);
      return { success: true, data: response };
    } catch (error) {
      console.error(`Failed to fetch user ${userId}:`, error);
      return { success: false, error: error.message };
    }
  }
}

export const usersService = new UsersService();