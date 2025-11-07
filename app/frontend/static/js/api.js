// Handles all API communication
const api = {
    baseUrl: '/api/v1',
    token: null,
    
    // User switching audit log
    switchLog: [],

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

        console.log(`🌐 API Request: ${method} ${endpoint}`, {
            hasToken: !!this.token,
            tokenPreview: this.token ? this.token.substring(0, 20) + '...' : 'none',
            bodySize: body ? JSON.stringify(body).length : 0
        });

        try {
            const response = await fetch(this.baseUrl + endpoint, config);
            
            console.log(`📡 API Response: ${method} ${endpoint}`, {
                status: response.status,
                statusText: response.statusText,
                ok: response.ok
            });
            
            if (!response.ok) {
                // Handle non-2xx responses
                let errorData;
                try {
                    errorData = await response.json();
                } catch {
                    errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
                }
                console.error('❌ API Error Response:', errorData);
                return { success: false, error: errorData };
            }
            const responseData = await response.json();
            console.log(`✅ API Success: ${method} ${endpoint}`, responseData);
            return { success: true, data: responseData };
        } catch (error) {
            console.error('❌ Fetch Error:', error);
            return { success: false, error: { detail: 'Network error - please check your connection' } };
        }
    },

    setToken(token) {
        const previousToken = this.token;
        this.token = token;
        localStorage.setItem('authToken', token);
        
        // Log token changes for debugging
        console.log('🔑 Token Updated:', {
            hasToken: !!token,
            tokenLength: token ? token.length : 0,
            previousTokenPresent: !!previousToken,
            timestamp: new Date().toISOString()
        });
    },

    clearToken() {
        const hadToken = !!this.token;
        this.token = null;
        localStorage.removeItem('authToken');
        
        console.log('🗑️ Token Cleared:', {
            hadPreviousToken: hadToken,
            timestamp: new Date().toISOString()
        });
    },
    
    // Enhanced login method with user switching support
    async login(email, password, isUserSwitch = false) {
        const loginAttempt = {
            email,
            timestamp: new Date().toISOString(),
            isUserSwitch,
            success: false
        };
        
        try {
            const response = await this.request('/auth/login', 'POST', { email, password });
            
            loginAttempt.success = response.success;
            loginAttempt.error = response.error;
            
            if (isUserSwitch) {
                this.switchLog.push(loginAttempt);
                this.logSwitchAttempt(loginAttempt);
            }
            
            return response;
        } catch (error) {
            loginAttempt.error = error;
            if (isUserSwitch) {
                this.switchLog.push(loginAttempt);
                this.logSwitchAttempt(loginAttempt);
            }
            throw error;
        }
    },
    
    logSwitchAttempt(attempt) {
        const logStyle = attempt.success 
            ? 'color: #2ecc71; font-weight: bold;' 
            : 'color: #e74c3c; font-weight: bold;';
            
        console.log(
            `%c🔄 USER SWITCH ${attempt.success ? 'SUCCESS' : 'FAILED'}`,
            logStyle,
            {
                email: attempt.email,
                timestamp: attempt.timestamp,
                error: attempt.error?.detail || null,
                totalSwitchAttempts: this.switchLog.length
            }
        );
    },
    
    getSwitchAuditLog() {
        return [...this.switchLog];
    },
    
    clearSwitchAuditLog() {
        const previousCount = this.switchLog.length;
        this.switchLog = [];
        console.log(`🗑️ Cleared ${previousCount} switch audit log entries`);
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
    
    // Development endpoints
    async getAllUsersForTesting() {
        return await this.request('/admin/users');
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
        return await this.request('/enterprises/create', 'POST', data);
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
    },

    // OpenAPI/Swagger endpoints
    async getOpenApiSpec() {
        try {
            const response = await fetch('/api/v1/openapi.json');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return { success: true, data: await response.json() };
        } catch (error) {
            console.error('Failed to fetch OpenAPI spec:', error);
            return { success: false, error: { detail: error.message } };
        }
    }
};

// Load token from storage on startup
api.token = localStorage.getItem('authToken');
