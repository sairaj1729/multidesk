import { apiService } from './api';

class AuthService {
  constructor() {
    this.tokenKey = 'access_token';
    this.userKey = 'user_data';
  }

  // Register new user
  async register(userData) {
    try {
      console.log('Attempting to register user:', userData);
      const response = await apiService.post('/api/auth/register', userData);
      console.log('Registration response:', response);
      return { success: true, data: response };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: error.message };
    }
  }

  // Login user
  async login(credentials) {
    try {
      const response = await apiService.post('/api/auth/login', credentials);
      
      if (response.access_token) {
        this.setToken(response.access_token);
        this.setUser(response.user);
      }
      
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Verify email with OTP
  async verifyEmail(email, otp) {
    try {
      const response = await apiService.post('/api/auth/verify-email', { email, otp });
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Resend verification OTP
  async resendVerificationOTP(email) {
    try {
      const response = await apiService.post('/api/auth/resend-verification', { email });
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Request password reset OTP
  async forgotPassword(email) {
    try {
      const response = await apiService.post('/api/auth/forgot-password', { email });
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Reset password with OTP
  async resetPassword(email, otp, newPassword) {
    try {
      const response = await apiService.post('/api/auth/reset-password', {
        email,
        otp,
        new_password: newPassword
      });
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Get current user info
  async getCurrentUser() {
    try {
      const response = await apiService.get('/api/auth/me');
      this.setUser(response);
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Token management
  setToken(token) {
    localStorage.setItem(this.tokenKey, token);
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  removeToken() {
    localStorage.removeItem(this.tokenKey);
  }

  // User management
  setUser(user) {
    localStorage.setItem(this.userKey, JSON.stringify(user));
  }

  getUser() {
    const userData = localStorage.getItem(this.userKey);
    return userData ? JSON.parse(userData) : null;
  }

  removeUser() {
    localStorage.removeItem(this.userKey);
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getToken();
  }

  // Check if user is verified
  isVerified() {
    const user = this.getUser();
    return user?.is_verified || false;
  }

  // Logout
  logout() {
    this.removeToken();
    this.removeUser();
  }
}

export const authService = new AuthService();