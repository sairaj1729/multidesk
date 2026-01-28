import { apiService } from './api';

class FilesService {
  constructor() {
    this.basePath = '/api/files';
  }

  async uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiService.request(
    `${this.basePath}/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  return response; // let caller decide success
}


  async getFiles(filters = {}, page = 1, size = 50) {
    try {
      // Build query parameters
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('size', size);
      
      // Add filters if provided
      if (filters.search) params.append('search', filters.search);
      if (filters.status) params.append('status', filters.status);
      if (filters.file_type) params.append('file_type', filters.file_type);
      
      const queryString = params.toString();
      const url = queryString ? `${this.basePath}/?${queryString}` : `${this.basePath}/`;
      
      const response = await apiService.get(url);
      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to fetch files:', error);
      return { success: false, error: error.message };
    }
  }

  async getFileById(fileId) {
    try {
      const response = await apiService.get(`${this.basePath}/${fileId}`);
      return { success: true, data: response };
    } catch (error) {
      console.error(`Failed to fetch file ${fileId}:`, error);
      return { success: false, error: error.message };
    }
  }

  async deleteFile(fileId) {
    try {
      const response = await apiService.delete(`${this.basePath}/${fileId}`);
      return { success: true, data: response };
    } catch (error) {
      console.error(`Failed to delete file ${fileId}:`, error);
      return { success: false, error: error.message };
    }
  }

  async downloadFile(fileId) {
    try {
      const response = await apiService.request(`${this.basePath}/${fileId}/download`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/octet-stream'
        }
      });
      
      return { success: true, data: response };
    } catch (error) {
      console.error(`Failed to download file ${fileId}:`, error);
      return { success: false, error: error.message };
    }
  }
}

export const filesService = new FilesService();