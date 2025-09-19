// Main application logic
const app = {
    user: null,
    adminState: {
        currentTab: 'users',
        auditLog: [],
        rawJsonVisible: {
            users: false,
            enterprises: false
        }
    },
    currentUsers: null,
    currentEnterprises: null,

    async init() {
        // Load stored token first
        const storedToken = localStorage.getItem('authToken');
        if (storedToken) {
            api.setToken(storedToken);
        }
        
        // Load stored audit log
        const storedAuditLog = localStorage.getItem('adminAuditLog');
        if (storedAuditLog) {
            try {
                this.adminState.auditLog = JSON.parse(storedAuditLog);
            } catch (e) {
                console.error('Error parsing stored audit log:', e);
                this.adminState.auditLog = [];
            }
        }
        
        // Check for authenticated session
        if (api.token) {
            try {
                const response = await api.getCurrentUser();
                if (response.success) {
                    this.user = response.data;
                } else {
                    // Token is invalid, clear it
                    console.log('Token invalid, clearing...');
                    api.clearToken();
                }
            } catch (error) {
                console.error('Error checking user session:', error);
                api.clearToken();
            }
        }

        this.setupRoutes();
        await ui.renderSidebar(!!this.user);
        router.handle();
    },

    setupRoutes() {
        router.add('/', () => ui.render('<h2>Dashboard</h2><p>Welcome to XenToba!</p>'));
        router.add('/enterprises', () => this.showEnterprisesPage());
        router.add('/tax-planner', () => this.showTaxPlannerPage());
        router.add('/admin', () => this.showAdminPage());
        router.add('/auth', () => this.showAuthPage());
        router.add('/profile', () => this.showProfilePage());
        router.add('/api-explorer', () => this.showApiExplorerPage());
        router.add('/google-callback', () => this.handleGoogleCallback());
        router.add('/404', () => ui.render('<h2>404 Not Found</h2>'));
    },

    showAuthPage(initialView = 'login') {
        ui.render(components.createAuthContainer(initialView));
        this.attachAuthEventListeners();
    },

    attachAuthEventListeners() {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = new FormData(loginForm);
                await this.login(data.get('email'), data.get('password'));
            });
        }

        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = new FormData(registerForm);
                const userData = Object.fromEntries(data.entries());
                await this.register(userData);
            });
        }
        
        const googleLoginBtn = document.getElementById('google-login-btn');
        if (googleLoginBtn) {
            googleLoginBtn.addEventListener('click', async () => {
                console.log('Google login clicked');
                const response = await api.getGoogleLoginUrl();
                console.log('Google auth response:', response);
                if (response.success) {
                    window.location.href = response.data.auth_url;
                } else {
                    ui.showNotification('Failed to get Google login URL', 'error');
                }
            });
        }

        document.querySelectorAll('.auth-toggle').forEach(el => {
            el.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.showAuthPage(view);
            });
        });
    },

    async login(email, password) {
        console.log('Login attempt:', email);
        // Show loading state
        const submitBtn = document.querySelector('#login-form button[type="submit"]');
        const originalText = submitBtn?.textContent;
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Logging in...';
        }

        const response = await api.login(email, password);
        console.log('Login response:', response);
        
        // Restore button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }

        if (response.success) {
            api.setToken(response.data.access_token);
            const userResponse = await api.getCurrentUser();
            console.log('Current user response:', userResponse);
            if (userResponse.success) {
                this.user = userResponse.data;
            }
            await this.init(); // Re-initialize the app
            router.navigate('/');
            ui.showNotification('Login successful!', 'success');
        } else {
            const errorMsg = response.error?.detail || 'Login failed. Please check your credentials.';
            console.error('Login error:', errorMsg);
            ui.showNotification(errorMsg, 'error');
        }
    },

    async register(userData) {
        // Show loading state
        const submitBtn = document.querySelector('#register-form button[type="submit"]');
        const originalText = submitBtn?.textContent;
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating account...';
        }

        const response = await api.register(userData);
        
        // Restore button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }

        if (response.success) {
            ui.showNotification('Registration successful! Please log in.', 'success');
            this.showAuthPage('login');
        } else {
            const errorMsg = response.error?.detail || 'Registration failed. Please try again.';
            ui.showNotification(errorMsg, 'error');
        }
    },

    handleGoogleCallback() {
        console.log('Handling Google OAuth callback');
        console.log('Current URL:', window.location.href);
        
        // Show loading message
        ui.render('<div class="loading-container"><h2>Completing Google Sign-In...</h2><p>Please wait while we log you in.</p></div>');
        
        // Parse tokens from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const accessToken = urlParams.get('access_token');
        const refreshToken = urlParams.get('refresh_token');
        
        console.log('Access token received:', accessToken ? 'Yes' : 'No');
        console.log('Refresh token received:', refreshToken ? 'Yes' : 'No');
        
        if (accessToken && refreshToken) {
            // Store tokens
            api.setToken(accessToken);
            localStorage.setItem('refreshToken', refreshToken);
            
            // Clean up URL to remove tokens from address bar
            window.history.replaceState({}, document.title, '/google-callback');
            
            // Get user info and complete login
            this.completeGoogleLogin();
        } else {
            console.error('Missing tokens in callback URL');
            console.log('URL search params:', window.location.search);
            ui.showNotification('Google login failed - missing authentication tokens', 'error');
            router.navigate('/auth');
        }
    },

    async completeGoogleLogin() {
        try {
            // Get current user info
            const userResponse = await api.getCurrentUser();
            console.log('Google login user response:', userResponse);
            
            if (userResponse.success) {
                this.user = userResponse.data;
                await this.init(); // Re-initialize the app
                router.navigate('/');
                ui.showNotification('Google login successful!', 'success');
            } else {
                console.error('Failed to get user info after Google login');
                ui.showNotification('Google login failed - could not get user information', 'error');
                api.clearToken();
                router.navigate('/auth');
            }
        } catch (error) {
            console.error('Error completing Google login:', error);
            ui.showNotification('Google login failed - please try again', 'error');
            api.clearToken();
            router.navigate('/auth');
        }
    },

    async showEnterprisesPage() {
        const response = await api.getEnterprises();
        if (response.success) {
            ui.render(components.createEnterpriseList(response.data));
            this.attachEnterpriseEventListeners();
        } else {
            ui.render('<h2>Could not load enterprises.</h2>');
        }
    },

    attachEnterpriseEventListeners() {
        // Add enterprise button
        const addBtn = document.getElementById('add-enterprise-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                ui.showModal(components.createEnterpriseForm(), 'Add Enterprise');
                this.handleEnterpriseFormSubmit();
            });
        }

        // Edit enterprise buttons (on cards)
        document.querySelectorAll('.enterprise-card .edit-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const enterpriseCard = e.target.closest('.enterprise-card');
                const id = enterpriseCard.dataset.enterpriseId;
                
                if (id) {
                    const response = await api.getEnterprise(id);
                    if (response.success) {
                        ui.showModal(components.createEnterpriseForm(response.data), `Edit Enterprise`);
                        this.handleEnterpriseFormSubmit(id);
                    } else {
                        ui.showNotification('Could not load enterprise details', 'error');
                    }
                }
            });
        });

        // Delete enterprise buttons (on cards)
        document.querySelectorAll('.enterprise-card .delete-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const enterpriseCard = e.target.closest('.enterprise-card');
                const id = enterpriseCard.dataset.enterpriseId;
                const name = enterpriseCard.querySelector('h3').textContent;
                
                if (id && confirm(`Are you sure you want to delete "${name}"?`)) {
                    const response = await api.deleteEnterprise(id);
                    if (response.success) {
                        this.showEnterprisesPage();
                        ui.showNotification('Enterprise deleted successfully', 'success');
                    } else {
                        ui.showNotification('Could not delete enterprise', 'error');
                    }
                }
            });
        });

        // Click on enterprise card to view details (optional)
        document.querySelectorAll('.enterprise-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Only trigger if clicking the card itself, not buttons
                if (!e.target.classList.contains('btn') && !e.target.closest('.btn')) {
                    const id = card.dataset.enterpriseId;
                    // Could navigate to enterprise details page in the future
                    console.log('Enterprise card clicked:', id);
                }
            });
        });
    },

    async showProfilePage() {
        try {
            ui.render('<div class="loading-container"><h2>Loading Profile...</h2><p>Please wait while we load your profile information.</p></div>');
            
            const response = await api.getUserProfile();
            console.log('Profile response:', response);
            
            if (response.success) {
                ui.render(components.createProfilePage(response.data));
                this.attachProfileEventListeners();
            } else {
                ui.render('<h2>Could not load profile.</h2><p>Please try again later.</p>');
                ui.showNotification('Failed to load profile', 'error');
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            ui.render('<h2>Error loading profile.</h2><p>Please try again later.</p>');
            ui.showNotification('Error loading profile', 'error');
        }
    },

    attachProfileEventListeners() {
        // Handle "View Details" buttons for enterprises in profile
        document.querySelectorAll('.view-enterprise-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = e.target.dataset.id || e.target.closest('.view-enterprise-btn').dataset.id;
                
                if (id) {
                    // Navigate to enterprise page or show enterprise details
                    router.navigate(`/enterprises`); // Will show enterprise list where user can see full details
                    // Alternative: could show enterprise details modal
                    // const response = await api.getEnterprise(id);
                    // if (response.success) {
                    //     ui.showModal(components.createEnterpriseDetails(response.data), 'Enterprise Details');
                    // }
                }
            });
        });
    },

    showEditProfile() {
        // TODO: Implement edit profile modal
        ui.showNotification('Edit profile feature coming soon!', 'info');
    },

    showChangePassword() {
        // TODO: Implement change password modal
        ui.showNotification('Change password feature coming soon!', 'info');
    },

    async showTaxPlannerPage() {
        const response = await api.getTaxProjects();
        if (response.success) {
            ui.render(components.createTaxPlannerDashboard(response.data));
            this.attachTaxPlannerEventListeners();
        } else {
            ui.render('<h2>Could not load tax planner data.</h2>');
        }
    },

    attachTaxPlannerEventListeners() {
        document.getElementById('add-project-btn').addEventListener('click', () => {
            ui.showModal(components.createTaxProjectForm(), 'Add Tax Project');
            this.handleTaxProjectFormSubmit();
        });

        document.querySelectorAll('.edit-project-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const response = await api.getTaxProject(id);
                if (response.success) {
                    ui.showModal(components.createTaxProjectForm(response.data), 'Edit Tax Project');
                    this.handleTaxProjectFormSubmit(id);
                }
            });
        });

        document.querySelectorAll('.delete-project-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                if (confirm('Are you sure you want to delete this tax project?')) {
                    await api.deleteTaxProject(id);
                    this.showTaxPlannerPage();
                }
            });
        });
    },

    handleTaxProjectFormSubmit(id = null) {
        const form = document.getElementById('tax-project-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const response = id 
                ? await api.updateTaxProject(id, data)
                : await api.createTaxProject(data);

            if (response.success) {
                ui.closeModal();
                this.showTaxPlannerPage();
                ui.showNotification(`Tax project ${id ? 'updated' : 'created'} successfully!`, 'success');
            } else {
                ui.showNotification('An error occurred.', 'error');
            }
        });
    },

    handleEnterpriseFormSubmit(id = null) {
        const form = document.getElementById('enterprise-form');
        if (!form) {
            console.error('Enterprise form not found');
            return;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Convert tax_year to number
            if (data.tax_year) {
                data.tax_year = parseInt(data.tax_year, 10);
            }
            
            // Basic validation
            if (!data.name || !data.email || !data.type) {
                ui.showNotification('Please fill in all required fields (Name, Email, Type)', 'error');
                return;
            }
            
            if (!data.country || !data.city) {
                ui.showNotification('Please fill in all required fields (Country, City)', 'error');
                return;
            }

            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = id ? 'Updating...' : 'Creating...';
            submitBtn.disabled = true;

            try {
                // Debug: Log the data being sent
                console.log('Sending enterprise data:', data);
                
                const response = id 
                    ? await api.updateEnterprise(id, data)
                    : await api.createEnterprise(data);

                console.log('API response:', response);

                if (response.success) {
                    ui.closeModal();
                    this.showEnterprisesPage();
                    ui.showNotification(`Enterprise ${id ? 'updated' : 'created'} successfully!`, 'success');
                } else {
                    console.error('API error details:', response);
                    ui.showNotification(response.error || response.detail || 'An error occurred', 'error');
                }
            } catch (error) {
                console.error('Enterprise form submit error:', error);
                ui.showNotification('Network error occurred', 'error');
            } finally {
                // Reset button state
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    },

    async showAdminPage() {
        console.log('showAdminPage called');
        
        // Simple test - bypass all authentication for now
        const simpleContent = `
            <div style="padding: 20px; background: white; border-radius: 8px; margin: 20px;">
                <h1 style="color: #333;">Admin Dashboard Test</h1>
                <p>This is a simple test to verify rendering works.</p>
                <p>Current time: ${new Date().toLocaleString()}</p>
                <button onclick="alert('Button clicked!')" style="padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px;">Test Button</button>
            </div>
        `;
        
        console.log('About to render content:', simpleContent);
        ui.render(simpleContent);
        console.log('Content rendered');
        
        return; // Exit early for testing
        
        /*
        ui.showLoading('Loading admin dashboard...');
        
        try {
            // Check user permissions first
            const currentUserResponse = await api.getCurrentUser();
            
            if (!currentUserResponse.success) {
                ui.render(`
                    <div class="auth-required-page">
                        <div class="auth-card">
                            <i class="material-icons" style="font-size: 4rem; color: #e74c3c; margin-bottom: 1rem;">lock</i>
                            <h2>Authentication Required</h2>
                            <p>You need to log in to access the admin dashboard.</p>
                            <div class="auth-actions">
                                <button class="btn btn-primary" onclick="router.go('/auth')">
                                    <i class="material-icons">login</i> Go to Login
                                </button>
                                <button class="btn btn-outline" onclick="location.reload()">
                                    <i class="material-icons">refresh</i> Try Again
                                </button>
                            </div>
                        </div>
                    </div>
                `);
                return;
            }
            
            const currentUser = currentUserResponse.data;
            
            // TODO: Re-enable proper admin checking once backend implements is_superuser field
            // For now, allow any authenticated user to access admin page for testing
            
            // Initialize with empty data first, then load asynchronously
            const stats = { total_users: 0, total_enterprises: 0, total_projects: 0 };
            const users = [];
            const enterprises = [];
            
            // Initialize empty audit log
            this.adminState.auditLog = JSON.parse(localStorage.getItem('adminAuditLog') || '[]');
            
            console.log('Creating admin dashboard with:', { users, stats, currentUser });
            
            // Test with a simple HTML first to see if rendering works
            const testHtml = `
                <div class="admin-dashboard">
                    <h1>Admin Dashboard Test</h1>
                    <p>User: ${currentUser.email}</p>
                    <p>Users count: ${users.length}</p>
                    <p>Current time: ${new Date().toLocaleString()}</p>
                </div>
            `;
            
            console.log('Test HTML:', testHtml);
            ui.render(testHtml);
            
            // TODO: Replace with full dashboard once we confirm rendering works
            // const dashboardHtml = components.createAdminDashboard(users, stats, currentUser);
            // console.log('Generated HTML length:', dashboardHtml ? dashboardHtml.length : 0);
            // ui.render(dashboardHtml);
            
            // this.attachAdminEventListeners();
            
            // Now load data asynchronously
            this.loadAdminData();
            
        } catch (error) {
            console.error('Error loading admin page:', error);
            ui.render(`
                <div class="error-page">
                    <div class="error-card">
                        <i class="material-icons" style="font-size: 4rem; color: #e74c3c; margin-bottom: 1rem;">error</i>
                        <h2>Error Loading Admin Page</h2>
                        <p>Something went wrong while loading the admin dashboard.</p>
                        <details class="error-details">
                            <summary>Technical Details</summary>
                            <pre>${error.message}</pre>
                        </details>
                        <div class="auth-actions">
                            <button class="btn btn-primary" onclick="location.reload()">
                                <i class="material-icons">refresh</i> Try Again
                            </button>
                            <button class="btn btn-outline" onclick="router.go('/home')">
                                <i class="material-icons">home</i> Go Home
                            </button>
                        </div>
                    </div>
                </div>
            `);
        }
        */
    },

    async loadAdminData() {
        try {
            // Load users data
            this.loadUsers();
            
            // Load enterprises data
            this.loadEnterprises();
            
            // Load auth info
            this.refreshAuthInfo();
            
            // Render audit log
            this.renderAuditLog();
            
        } catch (error) {
            console.error('Error loading admin data:', error);
            ui.showNotification('Failed to load some admin data', 'warning');
        }
    },

    attachAdminEventListeners() {
        // Initialize admin state
        this.adminState = {
            currentTab: 'users',
            auditLog: JSON.parse(localStorage.getItem('adminAuditLog') || '[]')
        };

        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchAdminTab(tabName);
            });
        });

        // Auth debugging panel
        document.getElementById('refresh-token-btn')?.addEventListener('click', () => {
            this.refreshAuthInfo();
        });

        document.getElementById('update-token-btn')?.addEventListener('click', () => {
            const newToken = document.getElementById('manual-token').value.trim();
            if (newToken) {
                api.setToken(newToken);
                this.refreshAuthInfo();
                ui.showNotification('Token updated', 'success');
            }
        });

        // User management events
        this.attachUserManagementEvents();
        
        // Enterprise management events
        this.attachEnterpriseManagementEvents();
        
        // Audit log events
        this.attachAuditLogEvents();

        // Developer utilities
        this.attachDeveloperUtilities();

        // Load initial data for current tab
        this.loadAdminTabData(this.adminState.currentTab);
    },

    switchAdminTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-panel').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.adminState.currentTab = tabName;
        this.loadAdminTabData(tabName);
    },

    async loadAdminTabData(tabName) {
        switch (tabName) {
            case 'users':
                await this.loadUsers();
                break;
            case 'enterprises':
                await this.loadEnterprises();
                break;
            case 'auth':
                await this.refreshAuthInfo();
                break;
            case 'audit':
                this.renderAuditLog();
                break;
        }
    },

    attachUserManagementEvents() {
        // Add user button
        document.getElementById('add-user-btn')?.addEventListener('click', () => {
            ui.showModal(components.createUserForm(), 'Add User');
            this.handleUserFormSubmit();
        });

        // Search users
        document.getElementById('user-search')?.addEventListener('input', (e) => {
            this.searchUsers(e.target.value);
        });

        // Filter users by role
        document.getElementById('user-role-filter')?.addEventListener('change', (e) => {
            this.filterUsers('role', e.target.value);
        });

        // Filter users by status
        document.getElementById('user-status-filter')?.addEventListener('change', (e) => {
            this.filterUsers('status', e.target.value);
        });

        // Refresh users
        document.getElementById('refresh-users-btn')?.addEventListener('click', () => {
            this.loadUsers();
        });

        // Show raw JSON toggle
        document.getElementById('show-users-json')?.addEventListener('change', (e) => {
            this.toggleRawJSON('users', e.target.checked);
        });
    },

    attachEnterpriseManagementEvents() {
        // Add enterprise button
        document.getElementById('add-enterprise-btn')?.addEventListener('click', () => {
            ui.showModal(components.createEnterpriseForm(), 'Add Enterprise');
            this.handleEnterpriseFormSubmit();
        });

        // Search enterprises
        document.getElementById('enterprise-search')?.addEventListener('input', (e) => {
            this.searchEnterprises(e.target.value);
        });

        // Refresh enterprises
        document.getElementById('refresh-enterprises-btn')?.addEventListener('click', () => {
            this.loadEnterprises();
        });

        // Show raw JSON toggle
        document.getElementById('show-enterprises-json')?.addEventListener('change', (e) => {
            this.toggleRawJSON('enterprises', e.target.checked);
        });
    },

    attachAuditLogEvents() {
        // Clear audit log
        document.getElementById('clear-audit-log')?.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear the audit log?')) {
                this.clearAuditLog();
            }
        });

        // Show audit details
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('audit-detail-btn')) {
                const logIndex = e.target.dataset.index;
                this.showAuditDetails(logIndex);
            }
        });
    },

    attachDeveloperUtilities() {
        // Copy buttons for IDs
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('copy-id-btn')) {
                const id = e.target.dataset.id;
                navigator.clipboard.writeText(id).then(() => {
                    ui.showNotification('ID copied to clipboard', 'success');
                });
            }
        });

        // Quick links
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('view-user-enterprises')) {
                const userId = e.target.dataset.userId;
                this.viewUserEnterprises(userId);
            }
        });
    },

    handleUserFormSubmit(id = null) {
        const form = document.getElementById('user-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Handle checkbox for is_active
            data.is_active = form.querySelector('input[name="is_active"]').checked;
            
            const response = id 
                ? await api.updateUser(id, data)
                : await api.createUser(data);

            if (response.success) {
                ui.closeModal();
                this.showAdminPage();
                ui.showNotification(`User ${id ? 'updated' : 'created'} successfully!`, 'success');
            } else {
                const errorMessage = response.error?.detail || 'An error occurred.';
                ui.showNotification(errorMessage, 'error');
            }
        });
    },

    // Load and manage users
    async loadUsers() {
        const container = document.getElementById('users-table-container');
        if (!container) return;

        container.innerHTML = '<div class="loading">Loading users...</div>';

        try {
            const response = await this.logAdminAction('GET', '/admin/users', null);
            
            if (response.success) {
                const users = response.data;
                this.currentUsers = users;
                this.renderUsersTable(users);
            } else {
                container.innerHTML = '<div class="error">Failed to load users</div>';
                ui.showNotification('Failed to load users', 'error');
            }
        } catch (error) {
            container.innerHTML = '<div class="error">Network error loading users</div>';
            ui.showNotification('Network error loading users', 'error');
        }
    },

    renderUsersTable(users) {
        const container = document.getElementById('users-table-container');
        if (!users || users.length === 0) {
            container.innerHTML = '<div class="empty-state">No users found</div>';
            return;
        }

        const tableHtml = `
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Email</th>
                        <th>Username</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>
                                ${user.id}
                                <button class="copy-id-btn" data-id="${user.id}" title="Copy ID">
                                    <i class="material-icons">content_copy</i>
                                </button>
                            </td>
                            <td>${user.email}</td>
                            <td>${user.username}</td>
                            <td>
                                <span class="role-badge ${user.is_superuser ? 'admin' : 'user'}">
                                    ${user.is_superuser ? 'Admin' : 'User'}
                                </span>
                            </td>
                            <td>
                                <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                                    ${user.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${new Date(user.created_at || Date.now()).toLocaleDateString()}</td>
                            <td class="actions">
                                <button class="btn btn-sm view-user-btn" data-id="${user.id}">View</button>
                                <button class="btn btn-sm edit-user-btn" data-id="${user.id}">Edit</button>
                                <button class="btn btn-sm btn-danger delete-user-btn" data-id="${user.id}">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHtml;
        this.attachUserTableEvents();
    },

    attachUserTableEvents() {
        // Edit user buttons
        document.querySelectorAll('.edit-user-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const user = this.currentUsers.find(u => u.id == id);
                if (user) {
                    ui.showModal(components.createUserForm(user), 'Edit User');
                    this.handleUserFormSubmit(id);
                }
            });
        });

        // View user buttons
        document.querySelectorAll('.view-user-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const user = this.currentUsers.find(u => u.id == id);
                if (user) {
                    ui.showModal(components.createUserDetailView(user), 'User Details');
                }
            });
        });

        // Delete user buttons
        document.querySelectorAll('.delete-user-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const user = this.currentUsers.find(u => u.id == id);
                if (user && confirm(`Are you sure you want to delete ${user.email}?`)) {
                    const response = await this.logAdminAction('DELETE', `/admin/users/${id}`, null);
                    if (response.success) {
                        this.loadUsers();
                        ui.showNotification('User deleted successfully!', 'success');
                    } else {
                        ui.showNotification('Error deleting user.', 'error');
                    }
                }
            });
        });
    },

    searchUsers(query) {
        if (!this.currentUsers) return;
        
        const filtered = this.currentUsers.filter(user => 
            user.email.toLowerCase().includes(query.toLowerCase()) ||
            user.username.toLowerCase().includes(query.toLowerCase())
        );
        
        this.renderUsersTable(filtered);
    },

    filterUsers(type, value) {
        if (!this.currentUsers) return;
        
        let filtered = this.currentUsers;
        
        if (value !== 'all') {
            if (type === 'role') {
                filtered = filtered.filter(user => 
                    value === 'admin' ? user.is_superuser : !user.is_superuser
                );
            } else if (type === 'status') {
                filtered = filtered.filter(user => 
                    value === 'active' ? user.is_active : !user.is_active
                );
            }
        }
        
        this.renderUsersTable(filtered);
    },

    // Load and manage enterprises
    async loadEnterprises() {
        const container = document.getElementById('enterprises-table-container');
        if (!container) return;

        container.innerHTML = '<div class="loading">Loading enterprises...</div>';

        try {
            const response = await this.logAdminAction('GET', '/enterprises/', null);
            
            if (response.success) {
                const enterprises = response.data;
                this.currentEnterprises = enterprises;
                this.renderEnterprisesTable(enterprises);
            } else {
                container.innerHTML = '<div class="error">Failed to load enterprises</div>';
                ui.showNotification('Failed to load enterprises', 'error');
            }
        } catch (error) {
            container.innerHTML = '<div class="error">Network error loading enterprises</div>';
            ui.showNotification('Network error loading enterprises', 'error');
        }
    },

    renderEnterprisesTable(enterprises) {
        const container = document.getElementById('enterprises-table-container');
        if (!enterprises || enterprises.length === 0) {
            container.innerHTML = '<div class="empty-state">No enterprises found</div>';
            return;
        }

        const tableHtml = `
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Owner</th>
                        <th>Status</th>
                        <th>Members</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${enterprises.map(enterprise => `
                        <tr>
                            <td>
                                ${enterprise.id}
                                <button class="copy-id-btn" data-id="${enterprise.id}" title="Copy ID">
                                    <i class="material-icons">content_copy</i>
                                </button>
                            </td>
                            <td>${enterprise.name}</td>
                            <td>${enterprise.type?.replace(/_/g, ' ') || 'N/A'}</td>
                            <td>${enterprise.owner_id || 'N/A'}</td>
                            <td>
                                <span class="status-badge ${enterprise.is_active ? 'active' : 'inactive'}">
                                    ${enterprise.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${enterprise.staff_ids?.length || 0} + ${enterprise.client_ids?.length || 0}</td>
                            <td>${new Date(enterprise.created_at || Date.now()).toLocaleDateString()}</td>
                            <td class="actions">
                                <button class="btn btn-sm view-enterprise-btn" data-id="${enterprise.id}">View</button>
                                <button class="btn btn-sm edit-enterprise-btn" data-id="${enterprise.id}">Edit</button>
                                <button class="btn btn-sm btn-danger delete-enterprise-btn" data-id="${enterprise.id}">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHtml;
        this.attachEnterpriseTableEvents();
    },

    attachEnterpriseTableEvents() {
        // View enterprise buttons
        document.querySelectorAll('.view-enterprise-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const enterprise = this.currentEnterprises.find(e => e.id == id);
                if (enterprise) {
                    ui.showModal(components.createEnterpriseDetailView(enterprise), 'Enterprise Details');
                }
            });
        });

        // Edit enterprise buttons  
        document.querySelectorAll('.edit-enterprise-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const enterprise = this.currentEnterprises.find(e => e.id == id);
                if (enterprise) {
                    ui.showModal(components.createEnterpriseForm(enterprise), 'Edit Enterprise');
                    this.handleEnterpriseFormSubmit(id);
                }
            });
        });

        // Delete enterprise buttons
        document.querySelectorAll('.delete-enterprise-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const enterprise = this.currentEnterprises.find(e => e.id == id);
                if (enterprise && confirm(`Are you sure you want to delete ${enterprise.name}?`)) {
                    const response = await this.logAdminAction('DELETE', `/enterprises/${id}`, null);
                    if (response.success) {
                        this.loadEnterprises();
                        ui.showNotification('Enterprise deleted successfully!', 'success');
                    } else {
                        ui.showNotification('Error deleting enterprise.', 'error');
                    }
                }
            });
        });
    },

    searchEnterprises(query) {
        if (!this.currentEnterprises) return;
        
        const filtered = this.currentEnterprises.filter(enterprise => 
            enterprise.name.toLowerCase().includes(query.toLowerCase()) ||
            (enterprise.type && enterprise.type.toLowerCase().includes(query.toLowerCase()))
        );
        
        this.renderEnterprisesTable(filtered);
    },

    // Auth debugging
    async refreshAuthInfo() {
        const container = document.getElementById('auth-debug-container');
        if (!container) return;

        try {
            const response = await api.getCurrentUser();
            const authInfo = {
                token: api.token ? `${api.token.substring(0, 20)}...` : 'No token',
                tokenLength: api.token ? api.token.length : 0,
                user: response.success ? response.data : null,
                error: response.success ? null : response.error
            };

            container.innerHTML = components.createAuthDebugPanel(authInfo);
        } catch (error) {
            container.innerHTML = '<div class="error">Failed to load auth info</div>';
        }
    },

    // Audit logging
    async logAdminAction(method, path, data) {
        const startTime = Date.now();
        
        try {
            const response = await api.request(path, method, data);
            const endTime = Date.now();
            
            const logEntry = {
                timestamp: new Date().toISOString(),
                method,
                path: `/api/v1${path}`,
                data,
                response,
                duration: endTime - startTime,
                status: response.success ? 200 : 400
            };
            
            this.adminState.auditLog.unshift(logEntry);
            
            // Keep only last 100 entries
            if (this.adminState.auditLog.length > 100) {
                this.adminState.auditLog = this.adminState.auditLog.slice(0, 100);
            }
            
            localStorage.setItem('adminAuditLog', JSON.stringify(this.adminState.auditLog));
            
            // Update audit tab if it's active
            if (this.adminState.currentTab === 'audit') {
                this.renderAuditLog();
            }
            
            return response;
        } catch (error) {
            const endTime = Date.now();
            
            const logEntry = {
                timestamp: new Date().toISOString(),
                method,
                path: `/api/v1${path}`,
                data,
                response: { success: false, error: { detail: error.message } },
                duration: endTime - startTime,
                status: 0
            };
            
            this.adminState.auditLog.unshift(logEntry);
            localStorage.setItem('adminAuditLog', JSON.stringify(this.adminState.auditLog));
            
            throw error;
        }
    },

    renderAuditLog() {
        const container = document.getElementById('audit-log-container');
        if (!container) return;

        if (this.adminState.auditLog.length === 0) {
            container.innerHTML = '<div class="empty-state">No audit log entries</div>';
            return;
        }

        const logHtml = this.adminState.auditLog.map((entry, index) => `
            <div class="audit-entry">
                <div class="audit-header">
                    <span class="audit-method ${entry.method.toLowerCase()}">${entry.method}</span>
                    <span class="audit-path">${entry.path}</span>
                    <span class="audit-status status-${entry.status >= 200 && entry.status < 300 ? 'success' : 'error'}">
                        ${entry.status || 'ERR'}
                    </span>
                    <span class="audit-duration">${entry.duration}ms</span>
                    <span class="audit-time">${new Date(entry.timestamp).toLocaleTimeString()}</span>
                </div>
                <button class="btn btn-sm audit-detail-btn" data-index="${index}">
                    View Details
                </button>
            </div>
        `).join('');

        container.innerHTML = logHtml;
    },

    showAuditDetails(logIndex) {
        const entry = this.adminState.auditLog[logIndex];
        if (entry) {
            ui.showModal(components.createAuditDetailView(entry), 'Audit Entry Details');
        }
    },

    clearAuditLog() {
        this.adminState.auditLog = [];
        localStorage.removeItem('adminAuditLog');
        this.renderAuditLog();
        ui.showNotification('Audit log cleared', 'success');
    },

    // Developer utilities
    toggleRawJSON(type, show) {
        const container = document.getElementById(`${type}-json-container`);
        if (!container) return;

        if (show) {
            const data = type === 'users' ? this.currentUsers : this.currentEnterprises;
            container.innerHTML = `<pre class="json-viewer">${JSON.stringify(data, null, 2)}</pre>`;
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    },

    viewUserEnterprises(userId) {
        // This would need backend support - adding to missing features list
        ui.showNotification('Feature requires backend support', 'warning');
    },

    handleEnterpriseFormSubmit(id = null) {
        const form = document.getElementById('enterprise-form');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const endpoint = id ? `/enterprises/${id}` : '/enterprises/create';
            const method = id ? 'PUT' : 'POST';
            
            const response = await this.logAdminAction(method, endpoint, data);

            if (response.success) {
                ui.closeModal();
                this.loadEnterprises();
                ui.showNotification(`Enterprise ${id ? 'updated' : 'created'} successfully!`, 'success');
            } else {
                const errorMessage = response.error?.detail || 'An error occurred.';
                ui.showNotification(errorMessage, 'error');
            }
        });
    },

    showApiExplorerPage() {
        ui.render(components.createApiExplorer());
        this.attachApiExplorerEventListeners();
        this.loadEndpointCatalog();
    },

    attachApiExplorerEventListeners() {
        // Initialize API Explorer state
        this.apiExplorer = {
            history: JSON.parse(localStorage.getItem('apiExplorerHistory') || '[]')
        };

        // Load request history
        this.renderApiHistory();

        // Example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const example = e.target.dataset.example;
                this.loadApiExample(example);
            });
        });

        // HTTP method change - show/hide body field
        document.getElementById('http-method').addEventListener('change', (e) => {
            const method = e.target.value;
            const bodyGroup = document.getElementById('request-body-group');
            if (['GET', 'DELETE'].includes(method)) {
                bodyGroup.style.display = 'none';
            } else {
                bodyGroup.style.display = 'block';
            }
        });

        // Auth checkbox
        document.getElementById('use-auth').addEventListener('change', (e) => {
            const tokenGroup = document.getElementById('auth-token-group');
            tokenGroup.style.display = e.target.checked ? 'block' : 'none';
        });

        // Send request button
        document.getElementById('send-request').addEventListener('click', () => {
            this.sendApiRequest();
        });

        // Clear request button
        document.getElementById('clear-request').addEventListener('click', () => {
            this.clearApiRequest();
        });

        // Clear history button
        document.getElementById('clear-history').addEventListener('click', () => {
            this.clearApiHistory();
        });

        // Refresh endpoints button
        document.getElementById('refresh-endpoints').addEventListener('click', () => {
            this.loadEndpointCatalog();
        });

        // Toggle catalog button (for mobile)
        const toggleBtn = document.getElementById('toggle-catalog');
        const catalogPanel = document.querySelector('.api-catalog-panel');
        const catalogOverlay = document.getElementById('catalog-overlay');
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleEndpointCatalog();
            });
        }

        // Toggle response button (for mobile)
        const toggleResponseBtn = document.getElementById('toggle-response');
        if (toggleResponseBtn) {
            toggleResponseBtn.addEventListener('click', () => {
                this.toggleResponsePanel();
            });
        }

        if (catalogOverlay) {
            catalogOverlay.addEventListener('click', () => {
                this.hideEndpointCatalog();
            });
        }

        // Close catalog on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && catalogPanel && catalogPanel.classList.contains('open')) {
                this.hideEndpointCatalog();
            }
        });

        // Update toggle button visibility based on screen size
        this.updateToggleButtonsVisibility();
        window.addEventListener('resize', () => {
            this.updateToggleButtonsVisibility();
        });

        // Initialize UI state
        document.getElementById('http-method').dispatchEvent(new Event('change'));
        document.getElementById('use-auth').dispatchEvent(new Event('change'));
    },

    updateToggleButtonsVisibility() {
        const toggleBtn = document.getElementById('toggle-catalog');
        const toggleResponseBtn = document.getElementById('toggle-response');
        
        if (toggleBtn) {
            if (window.innerWidth <= 1200) {
                toggleBtn.style.display = 'inline-flex';
            } else {
                toggleBtn.style.display = 'none';
                this.hideEndpointCatalog(); // Close catalog if screen gets larger
            }
        }

        if (toggleResponseBtn) {
            if (window.innerWidth <= 768) {
                toggleResponseBtn.style.display = 'inline-flex';
            } else {
                toggleResponseBtn.style.display = 'none';
            }
        }
    },

    toggleResponsePanel() {
        const responsePanel = document.querySelector('.api-response-panel');
        if (responsePanel) {
            const isHidden = responsePanel.style.display === 'none';
            
            if (isHidden) {
                responsePanel.style.display = 'block';
                responsePanel.scrollIntoView({ behavior: 'smooth' });
                document.getElementById('toggle-response').innerHTML = '<i class="material-icons">visibility_off</i> Hide Response';
            } else {
                responsePanel.style.display = 'none';
                document.getElementById('toggle-response').innerHTML = '<i class="material-icons">receipt_long</i> Show Response';
            }
        }
    },

    toggleEndpointCatalog() {
        const catalogPanel = document.querySelector('.api-catalog-panel');
        const catalogOverlay = document.getElementById('catalog-overlay');
        const toggleBtn = document.getElementById('toggle-catalog');
        
        if (catalogPanel && catalogOverlay && toggleBtn) {
            const isOpen = catalogPanel.classList.contains('open');
            
            if (isOpen) {
                this.hideEndpointCatalog();
            } else {
                this.showEndpointCatalog();
            }
        }
    },

    showEndpointCatalog() {
        const catalogPanel = document.querySelector('.api-catalog-panel');
        const catalogOverlay = document.getElementById('catalog-overlay');
        const toggleBtn = document.getElementById('toggle-catalog');
        
        if (catalogPanel && catalogOverlay && toggleBtn) {
            catalogPanel.classList.add('open');
            catalogOverlay.classList.add('active');
            toggleBtn.innerHTML = '<i class="material-icons">close</i> Hide Endpoints';
            
            // Prevent body scroll when catalog is open on mobile
            document.body.style.overflow = 'hidden';
        }
    },

    hideEndpointCatalog() {
        const catalogPanel = document.querySelector('.api-catalog-panel');
        const catalogOverlay = document.getElementById('catalog-overlay');
        const toggleBtn = document.getElementById('toggle-catalog');
        
        if (catalogPanel && catalogOverlay && toggleBtn) {
            catalogPanel.classList.remove('open');
            catalogOverlay.classList.remove('active');
            toggleBtn.innerHTML = '<i class="material-icons">menu_open</i> Show Endpoints';
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
    },

    loadApiExample(example) {
        const examples = {
            health: {
                method: 'GET',
                path: '/health',
                headers: {},
                params: {},
                body: null
            },
            login: {
                method: 'POST',
                path: '/auth/login',
                headers: {},
                params: {},
                body: {
                    "email": "user@example.com",
                    "password": "Password@123"
                }
            },
            register: {
                method: 'POST',
                path: '/auth/register',
                headers: {},
                params: {},
                body: {
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "password": "Password@123"
                }
            },
            enterprises: {
                method: 'GET',
                path: '/enterprises/',
                headers: {},
                params: {},
                body: null
            },
            users: {
                method: 'GET',
                path: '/admin/users',
                headers: {},
                params: {},
                body: null
            }
        };

        const config = examples[example];
        if (!config) return;

        // Set form values
        document.getElementById('http-method').value = config.method;
        document.getElementById('endpoint-path').value = config.path;
        document.getElementById('request-headers').value = JSON.stringify(config.headers, null, 2);
        document.getElementById('query-params').value = JSON.stringify(config.params, null, 2);
        
        if (config.body) {
            document.getElementById('request-body').value = JSON.stringify(config.body, null, 2);
        } else {
            document.getElementById('request-body').value = '';
        }

        // Trigger method change to show/hide body
        document.getElementById('http-method').dispatchEvent(new Event('change'));

        // Show notification
        ui.showNotification(`Loaded ${example} example`, 'info');
    },

    async sendApiRequest() {
        const sendBtn = document.getElementById('send-request');
        const originalText = sendBtn.innerHTML;
        
        try {
            // Show loading state
            sendBtn.innerHTML = '<i class="material-icons">hourglass_empty</i> Sending...';
            sendBtn.disabled = true;

            // Get form values
            const method = document.getElementById('http-method').value;
            const path = document.getElementById('endpoint-path').value;
            const useAuth = document.getElementById('use-auth').checked;
            const customToken = document.getElementById('auth-token').value.trim();

            // Parse JSON fields
            let headers = {};
            let queryParams = {};
            let body = null;

            try {
                const headersText = document.getElementById('request-headers').value.trim();
                if (headersText) {
                    headers = JSON.parse(headersText);
                }
            } catch (error) {
                throw new Error('Invalid JSON in headers');
            }

            try {
                const paramsText = document.getElementById('query-params').value.trim();
                if (paramsText) {
                    queryParams = JSON.parse(paramsText);
                }
            } catch (error) {
                throw new Error('Invalid JSON in query parameters');
            }

            if (!['GET', 'DELETE'].includes(method)) {
                const bodyText = document.getElementById('request-body').value.trim();
                if (bodyText) {
                    try {
                        body = JSON.parse(bodyText);
                    } catch (error) {
                        throw new Error('Invalid JSON in request body');
                    }
                }
            }

            // Build URL with query parameters
            let fullPath = path;
            if (Object.keys(queryParams).length > 0) {
                const queryString = new URLSearchParams(queryParams).toString();
                fullPath += (path.includes('?') ? '&' : '?') + queryString;
            }

            // Prepare request
            const requestConfig = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                }
            };

            if (body) {
                requestConfig.body = JSON.stringify(body);
            }

            // Handle authentication
            if (useAuth) {
                const token = customToken || api.token;
                if (token) {
                    requestConfig.headers['Authorization'] = `Bearer ${token}`;
                }
            }

            // Record request start time
            const startTime = Date.now();

            // Make request
            const response = await fetch(`/api/v1${fullPath}`, requestConfig);
            
            // Record response time
            const responseTime = Date.now() - startTime;

            // Parse response
            let responseData;
            const responseText = await response.text();
            try {
                responseData = responseText ? JSON.parse(responseText) : {};
            } catch (error) {
                responseData = { _rawResponse: responseText };
            }

            // Create response object
            const apiResponse = {
                status: response.status,
                statusText: response.statusText,
                ok: response.ok,
                headers: Object.fromEntries(response.headers.entries()),
                data: responseData,
                responseTime
            };

            // Display response
            this.displayApiResponse(apiResponse);

            // Add to history
            this.addToApiHistory({
                timestamp: new Date().toISOString(),
                method,
                path: fullPath,
                request: {
                    headers: requestConfig.headers,
                    body: body
                },
                response: apiResponse
            });

        } catch (error) {
            console.error('API request error:', error);
            this.displayApiResponse({
                status: 0,
                statusText: 'Request Failed',
                ok: false,
                headers: {},
                data: { error: error.message },
                responseTime: 0
            });
            
            ui.showNotification(`Request failed: ${error.message}`, 'error');
        } finally {
            // Reset button state
            sendBtn.innerHTML = originalText;
            sendBtn.disabled = false;
        }
    },

    clearApiRequest() {
        document.getElementById('http-method').value = 'GET';
        document.getElementById('endpoint-path').value = '/health';
        document.getElementById('request-headers').value = '';
        document.getElementById('query-params').value = '';
        document.getElementById('request-body').value = '';
        document.getElementById('use-auth').checked = true;
        document.getElementById('auth-token').value = '';
        
        // Clear response
        document.getElementById('response-content').innerHTML = `
            <div class="response-placeholder">
                <i class="material-icons">http</i>
                <p>Send a request to see the response here</p>
            </div>
        `;
        document.getElementById('response-status').textContent = 'Ready to send request';
        document.getElementById('response-status').className = 'response-status';
        
        // Trigger change events
        document.getElementById('http-method').dispatchEvent(new Event('change'));
        document.getElementById('use-auth').dispatchEvent(new Event('change'));
    },

    displayApiResponse(response) {
        const statusElement = document.getElementById('response-status');
        const contentElement = document.getElementById('response-content');

        // Update status
        const statusClass = response.ok ? 'success' : 'error';
        statusElement.textContent = `${response.status} ${response.statusText} (${response.responseTime}ms)`;
        statusElement.className = `response-status ${statusClass}`;

        // Format response content
        const responseHtml = `
            <div class="response-details">
                <div class="response-section">
                    <h4><i class="material-icons">info</i> Status</h4>
                    <div class="status-badge ${statusClass}">
                        ${response.status} ${response.statusText}
                    </div>
                    <div class="response-time">Response time: ${response.responseTime}ms</div>
                </div>

                <div class="response-section">
                    <h4><i class="material-icons">http</i> Headers</h4>
                    <pre class="code-block">${JSON.stringify(response.headers, null, 2)}</pre>
                </div>

                <div class="response-section">
                    <h4><i class="material-icons">data_object</i> Body</h4>
                    <pre class="code-block">${JSON.stringify(response.data, null, 2)}</pre>
                </div>
            </div>
        `;

        contentElement.innerHTML = responseHtml;
    },

    addToApiHistory(entry) {
        this.apiExplorer.history.unshift(entry);
        
        // Keep only last 50 entries
        if (this.apiExplorer.history.length > 50) {
            this.apiExplorer.history = this.apiExplorer.history.slice(0, 50);
        }

        // Save to localStorage
        localStorage.setItem('apiExplorerHistory', JSON.stringify(this.apiExplorer.history));
        
        // Re-render history
        this.renderApiHistory();
    },

    renderApiHistory() {
        const historyElement = document.getElementById('request-history');
        
        if (!this.apiExplorer.history.length) {
            historyElement.innerHTML = `
                <div class="history-placeholder">
                    <p>Request history will appear here</p>
                </div>
            `;
            return;
        }

        const historyHtml = this.apiExplorer.history.map(entry => {
            const statusClass = entry.response.ok ? 'success' : 'error';
            const timestamp = new Date(entry.timestamp).toLocaleString();
            
            return `
                <div class="history-entry" data-entry='${JSON.stringify(entry).replace(/'/g, "&apos;")}'>
                    <div class="history-header">
                        <div class="history-method">${entry.method}</div>
                        <div class="history-path">${entry.path}</div>
                        <div class="history-status ${statusClass}">${entry.response.status}</div>
                    </div>
                    <div class="history-time">${timestamp}</div>
                    <button class="btn btn-sm btn-outline replay-btn" onclick="app.replayApiRequest(this)">
                        <i class="material-icons">replay</i> Replay
                    </button>
                </div>
            `;
        }).join('');

        historyElement.innerHTML = historyHtml;
    },

    replayApiRequest(button) {
        const entryData = button.closest('.history-entry').dataset.entry;
        const entry = JSON.parse(entryData.replace(/&apos;/g, "'"));
        
        // Extract path and query parameters
        const [basePath, queryString] = entry.path.split('?');
        const queryParams = {};
        
        if (queryString) {
            const params = new URLSearchParams(queryString);
            for (const [key, value] of params.entries()) {
                queryParams[key] = value;
            }
        }

        // Set form values
        document.getElementById('http-method').value = entry.method;
        document.getElementById('endpoint-path').value = basePath;
        
        // Set headers (excluding auto-added ones)
        const customHeaders = { ...entry.request.headers };
        delete customHeaders['Content-Type'];
        delete customHeaders['Authorization'];
        document.getElementById('request-headers').value = JSON.stringify(customHeaders, null, 2);
        
        document.getElementById('query-params').value = JSON.stringify(queryParams, null, 2);
        
        if (entry.request.body) {
            document.getElementById('request-body').value = JSON.stringify(entry.request.body, null, 2);
        } else {
            document.getElementById('request-body').value = '';
        }

        // Trigger change events
        document.getElementById('http-method').dispatchEvent(new Event('change'));
        
        ui.showNotification('Request replayed from history', 'info');
    },

    clearApiHistory() {
        if (confirm('Are you sure you want to clear the request history?')) {
            this.apiExplorer.history = [];
            localStorage.removeItem('apiExplorerHistory');
            this.renderApiHistory();
            ui.showNotification('Request history cleared', 'info');
        }
    },

    async loadEndpointCatalog() {
        const catalogElement = document.getElementById('endpoint-catalog');
        const refreshBtn = document.getElementById('refresh-endpoints');
        
        // Show loading state
        catalogElement.innerHTML = `
            <div class="catalog-loading">
                <i class="material-icons">hourglass_empty</i>
                <p>Loading endpoints...</p>
            </div>
        `;
        
        if (refreshBtn) {
            refreshBtn.disabled = true;
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="material-icons">hourglass_empty</i> Loading...';
        }

        try {
            const response = await api.getOpenApiSpec();
            
            if (response.success) {
                this.renderEndpointCatalog(response.data);
                ui.showNotification('Endpoint catalog refreshed', 'success');
            } else {
                catalogElement.innerHTML = `
                    <div class="catalog-error">
                        <i class="material-icons">error</i>
                        <p>Failed to load endpoints</p>
                        <small>${response.error?.detail || 'Unknown error'}</small>
                        <button class="btn btn-sm btn-primary" onclick="app.loadEndpointCatalog()">
                            <i class="material-icons">refresh</i> Retry
                        </button>
                    </div>
                `;
                ui.showNotification('Failed to load endpoint catalog', 'error');
            }
        } catch (error) {
            console.error('Error loading endpoint catalog:', error);
            catalogElement.innerHTML = `
                <div class="catalog-error">
                    <i class="material-icons">error</i>
                    <p>Network error</p>
                    <small>${error.message}</small>
                    <button class="btn btn-sm btn-primary" onclick="app.loadEndpointCatalog()">
                        <i class="material-icons">refresh</i> Retry
                    </button>
                </div>
            `;
        } finally {
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="material-icons">refresh</i> Refresh';
            }
        }
    },

    renderEndpointCatalog(openApiSpec) {
        const catalogElement = document.getElementById('endpoint-catalog');
        
        // Group endpoints by tags
        const endpointsByTag = {};
        const paths = openApiSpec.paths || {};
        
        Object.keys(paths).forEach(path => {
            const pathObject = paths[path];
            Object.keys(pathObject).forEach(method => {
                if (['get', 'post', 'put', 'patch', 'delete'].includes(method.toLowerCase())) {
                    const operation = pathObject[method];
                    const tags = operation.tags || ['Other'];
                    const tag = tags[0]; // Use first tag
                    
                    if (!endpointsByTag[tag]) {
                        endpointsByTag[tag] = [];
                    }
                    
                    endpointsByTag[tag].push({
                        method: method.toUpperCase(),
                        path: path,
                        summary: operation.summary || '',
                        description: operation.description || '',
                        operationId: operation.operationId || '',
                        parameters: operation.parameters || [],
                        requestBody: operation.requestBody || null,
                        responses: operation.responses || {}
                    });
                }
            });
        });

        // Sort tags alphabetically, but put common ones first
        const tagOrder = ['Auth', 'Users', 'Enterprises', 'Admin', 'Health'];
        const sortedTags = Object.keys(endpointsByTag).sort((a, b) => {
            const aIndex = tagOrder.indexOf(a);
            const bIndex = tagOrder.indexOf(b);
            
            if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
            if (aIndex !== -1) return -1;
            if (bIndex !== -1) return 1;
            return a.localeCompare(b);
        });

        // Create HTML for endpoint catalog
        let catalogHtml = '';
        
        if (sortedTags.length === 0) {
            catalogHtml = `
                <div class="catalog-empty">
                    <i class="material-icons">api_off</i>
                    <p>No endpoints found</p>
                </div>
            `;
        } else {
            catalogHtml = sortedTags.map(tag => {
                const endpoints = endpointsByTag[tag];
                const endpointItems = endpoints.map(endpoint => {
                    const methodClass = endpoint.method.toLowerCase();
                    return `
                        <div class="endpoint-item" 
                             data-method="${endpoint.method}" 
                             data-path="${endpoint.path}"
                             data-summary="${endpoint.summary}"
                             data-description="${endpoint.description}"
                             data-request-body='${JSON.stringify(endpoint.requestBody).replace(/'/g, "&apos;")}'>
                            <div class="endpoint-header">
                                <span class="endpoint-method ${methodClass}">${endpoint.method}</span>
                                <span class="endpoint-path">${endpoint.path}</span>
                            </div>
                            <div class="endpoint-summary">${endpoint.summary || 'No description'}</div>
                        </div>
                    `;
                }).join('');

                return `
                    <div class="endpoint-group">
                        <div class="endpoint-group-header">
                            <h4><i class="material-icons">folder</i> ${tag}</h4>
                            <span class="endpoint-count">${endpoints.length}</span>
                        </div>
                        <div class="endpoint-list">
                            ${endpointItems}
                        </div>
                    </div>
                `;
            }).join('');
        }

        catalogElement.innerHTML = catalogHtml;

        // Add click listeners to endpoint items
        document.querySelectorAll('.endpoint-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectEndpointFromCatalog(item);
            });
        });
    },

    selectEndpointFromCatalog(endpointElement) {
        const method = endpointElement.dataset.method;
        const path = endpointElement.dataset.path;
        const summary = endpointElement.dataset.summary;
        const requestBodyData = endpointElement.dataset.requestBody;

        // Set form values
        document.getElementById('http-method').value = method;
        document.getElementById('endpoint-path').value = path;
        
        // Clear other fields
        document.getElementById('request-headers').value = '';
        document.getElementById('query-params').value = '';
        document.getElementById('request-body').value = '';

        // Try to populate sample request body if available
        if (requestBodyData && requestBodyData !== 'null') {
            try {
                const requestBody = JSON.parse(requestBodyData.replace(/&apos;/g, "'"));
                if (requestBody && requestBody.content && requestBody.content['application/json']) {
                    const schema = requestBody.content['application/json'].schema;
                    if (schema && schema.example) {
                        document.getElementById('request-body').value = JSON.stringify(schema.example, null, 2);
                    } else if (schema && schema.properties) {
                        // Generate sample body from schema properties
                        const sampleBody = this.generateSampleFromSchema(schema);
                        if (sampleBody) {
                            document.getElementById('request-body').value = JSON.stringify(sampleBody, null, 2);
                        }
                    }
                }
            } catch (error) {
                console.error('Error parsing request body schema:', error);
            }
        }

        // Trigger method change to show/hide body field
        document.getElementById('http-method').dispatchEvent(new Event('change'));

        // Highlight selected endpoint
        document.querySelectorAll('.endpoint-item').forEach(item => {
            item.classList.remove('selected');
        });
        endpointElement.classList.add('selected');

        // Show notification
        ui.showNotification(`Selected ${method} ${path}`, 'info');

        // Close catalog on mobile after selection
        if (window.innerWidth <= 1200) {
            setTimeout(() => {
                this.hideEndpointCatalog();
            }, 500); // Small delay to show the selection feedback
        }
    },

    generateSampleFromSchema(schema) {
        if (!schema || !schema.properties) return null;

        const sample = {};
        Object.keys(schema.properties).forEach(key => {
            const property = schema.properties[key];
            switch (property.type) {
                case 'string':
                    if (property.format === 'email') {
                        sample[key] = 'user@example.com';
                    } else if (property.format === 'password') {
                        sample[key] = 'Password@123';
                    } else {
                        sample[key] = property.example || `example_${key}`;
                    }
                    break;
                case 'integer':
                    sample[key] = property.example || 1;
                    break;
                case 'number':
                    sample[key] = property.example || 1.0;
                    break;
                case 'boolean':
                    sample[key] = property.example !== undefined ? property.example : true;
                    break;
                case 'array':
                    sample[key] = property.example || [];
                    break;
                case 'object':
                    sample[key] = property.example || {};
                    break;
                default:
                    sample[key] = property.example || null;
            }
        });
        
        return Object.keys(sample).length > 0 ? sample : null;
    },

    async logout() {
        await api.logout();
        this.user = null;
        await ui.renderSidebar(false);
        router.navigate('/auth');
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
