/**
 * API utility for XenToba frontend
 * Handles all API calls to the backend
 */

class XenTobaAPI {
    constructor() {
        this.baseUrl = '/api/v1';
        this.token = localStorage.getItem('xentoba_token') || null;
    }

    /**
     * Set authentication token
     * @param {string} token - JWT token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('xentoba_token', token);
    }

    /**
     * Clear authentication token
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('xentoba_token');
    }

    /**
     * Get request headers including auth token if available
     * @returns {Object} Headers object
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Make API request
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {Object} data - Request body data
     * @returns {Promise} Promise resolving to response data
     */
    async request(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: this.getHeaders()
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const responseData = await response.json();

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: responseData.detail || 'An error occurred',
                    data: responseData
                };
            }

            return responseData;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * GET request wrapper
     * @param {string} endpoint - API endpoint
     * @returns {Promise} Promise resolving to response data
     */
    get(endpoint) {
        return this.request(endpoint, 'GET');
    }

    /**
     * POST request wrapper
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise} Promise resolving to response data
     */
    post(endpoint, data) {
        return this.request(endpoint, 'POST', data);
    }

    /**
     * PUT request wrapper
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise} Promise resolving to response data
     */
    put(endpoint, data) {
        return this.request(endpoint, 'PUT', data);
    }

    /**
     * DELETE request wrapper
     * @param {string} endpoint - API endpoint
     * @returns {Promise} Promise resolving to response data
     */
    delete(endpoint) {
        return this.request(endpoint, 'DELETE');
    }

    // AUTH ENDPOINTS
    async login(email, password) {
        const data = { email, password };
        const response = await this.post('/auth/login', data);
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        return response;
    }

    async register(userData) {
        return await this.post('/auth/register', userData);
    }

    async logout() {
        this.clearToken();
        return { success: true };
    }

    async getCurrentUser() {
        return await this.get('/auth/me');
    }
    
    getGoogleLoginUrl() {
        return `${this.baseUrl}/auth/google/login`;
    }
    
    processGoogleCallback(urlParams) {
        const params = new URLSearchParams(urlParams);
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        
        if (accessToken) {
            this.setToken(accessToken);
            return {
                success: true,
                access_token: accessToken,
                refresh_token: refreshToken
            };
        }
        
        return { success: false };
    }

    // ADMIN ENDPOINTS
    async getAllUsers(skip = 0, limit = 100) {
        return await this.get(`/admin/users/all?skip=${skip}&limit=${limit}`);
    }

    async getUserById(userId) {
        return await this.get(`/admin/users/${userId}`);
    }

    async createUser(userData) {
        return await this.post('/admin/users/create', userData);
    }

    async createSuperUser(userData) {
        return await this.post('/admin/users/create-super', userData);
    }

    async updateUser(userId, userData) {
        return await this.put(`/admin/users/update/${userId}`, userData);
    }

    async deleteUser(userId) {
        return await this.delete(`/admin/users/delete/${userId}`);
    }

    async updateUserSubscription(userId, subscriptionData) {
        return await this.post(`/admin/users/${userId}/subscription`, subscriptionData);
    }

    async createBatchUsers(usersData) {
        return await this.post('/admin/users/create/batch', { users: usersData });
    }

    // ENTERPRISE ENDPOINTS
    async getAllTentants() {
        return await this.get('/tentants/all');
    }

    async createTentant(enterpriseData) {
        return await this.post('/tentants/create', enterpriseData);
    }

    async getTentantById(enterpriseId) {
        return await this.get(`/tentants/${enterpriseId}`);
    }

    async updateTentant(enterpriseId, enterpriseData) {
        return await this.put(`/tentants/${enterpriseId}`, enterpriseData);
    }

    async deleteTentant(enterpriseId) {
        return await this.delete(`/tentants/${enterpriseId}`);
    }

    // PROFILE ENDPOINTS
    async getProfile() {
        return await this.get('/profile');
    }

    async updateProfile(profileData) {
        return await this.put('/profile/update', profileData);
    }

    async changePassword(passwordData) {
        return await this.put('/profile/change-password', passwordData);
    }
}

// Initialize global API instance
const api = new XenTobaAPI();
