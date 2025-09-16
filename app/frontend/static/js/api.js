// Handles all API communication
const api = {
    baseUrl: '/api/v1',
    token: null,

    async request(endpoint, method = 'GET', body = null) {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            method,
            headers,
            body: body ? JSON.stringify(body) : null
        };

        try {
            const response = await fetch(this.baseUrl + endpoint, config);
            if (!response.ok) {
                // Handle non-2xx responses
                let errorData;
                try {
                    errorData = await response.json();
                } catch {
                    errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
                }
                console.error('API Error:', errorData);
                return { success: false, error: errorData };
            }
            return { success: true, data: await response.json() };
        } catch (error) {
            console.error('Fetch Error:', error);
            return { success: false, error: { detail: 'Network error - please check your connection' } };
        }
    },

    setToken(token) {
        this.token = token;
        localStorage.setItem('authToken', token);
    },

    clearToken() {
        this.token = null;
        localStorage.removeItem('authToken');
    },

    // Auth endpoints
    async login(email, password) {
        return await this.request('/auth/login', 'POST', { email, password });
    },

    async register(userData) {
        return await this.request('/auth/register', 'POST', userData);
    },

    async getCurrentUser() {
        return await this.request('/users/me');
    },
    
    async getUserProfile() {
        return await this.request('/users/me/profile');
    },
    
    async getGoogleLoginUrl() {
        return this.request('/auth/google/login');
    },

    async logout() {
        this.clearToken();
        return { success: true };
    },
    
    // Health check
    async healthCheck() {
        return await this.request('/health');
    },

    // Enterprise endpoints
    async getEnterprises() {
        return await this.request('/enterprises/');
    },

    async createEnterprise(data) {
        return await this.request('/enterprises/', 'POST', data);
    },

    async getEnterprise(id) {
        return await this.request(`/enterprises/${id}`);
    },

    async updateEnterprise(id, data) {
        return await this.request(`/enterprises/${id}`, 'PUT', data);
    },

    async deleteEnterprise(id) {
        return await this.request(`/enterprises/${id}`, 'DELETE');
    },

    // Tax Planner endpoints
    async getTaxProjects() {
        return await this.request('/tax-planner/projects/');
    },

    async createTaxProject(data) {
        return await this.request('/tax-planner/projects/', 'POST', data);
    },

    async getTaxProject(id) {
        return await this.request(`/tax-planner/projects/${id}`);
    },

    async updateTaxProject(id, data) {
        return await this.request(`/tax-planner/projects/${id}`, 'PUT', data);
    },

    async deleteTaxProject(id) {
        return await this.request(`/tax-planner/projects/${id}`, 'DELETE');
    },

    // Admin endpoints
    async getAllUsers() {
        return await this.request('/admin/users/');
    },

    async createUser(data) {
        return await this.request('/admin/users/', 'POST', data);
    },

    async updateUser(id, data) {
        return await this.request(`/admin/users/${id}`, 'PUT', data);
    },

    async deleteUser(id) {
        return await this.request(`/admin/users/${id}`, 'DELETE');
    },

    async getSystemStats() {
        return await this.request('/admin/stats');
    }
};

// Load token from storage on startup
api.token = localStorage.getItem('authToken');
