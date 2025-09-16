// Main application logic
const app = {
    user: null,

    async init() {
        // Load stored token first
        const storedToken = localStorage.getItem('authToken');
        if (storedToken) {
            api.setToken(storedToken);
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
        ui.renderSidebar(!!this.user);
        router.handle();
    },

    setupRoutes() {
        router.add('/', () => ui.render('<h2>Dashboard</h2><p>Welcome to XenToba!</p>'));
        router.add('/enterprises', () => this.showEnterprisesPage());
        router.add('/tax-planner', () => this.showTaxPlannerPage());
        router.add('/admin', () => this.showAdminPage());
        router.add('/auth', () => this.showAuthPage());
        router.add('/profile', () => this.showProfilePage());
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
        const [usersResponse, statsResponse] = await Promise.all([
            api.getAllUsers(),
            api.getSystemStats()
        ]);

        if (usersResponse.success) {
            const stats = statsResponse.success ? statsResponse.data : {};
            ui.render(components.createAdminDashboard(usersResponse.data, stats));
            this.attachAdminEventListeners();
        } else {
            ui.render('<h2>Could not load admin data. You may not have admin permissions.</h2>');
        }
    },

    attachAdminEventListeners() {
        document.getElementById('add-user-btn').addEventListener('click', () => {
            ui.showModal(components.createUserForm(), 'Add User');
            this.handleUserFormSubmit();
        });

        document.querySelectorAll('.edit-user-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                const users = await api.getAllUsers();
                if (users.success) {
                    const user = users.data.find(u => u.id == id);
                    if (user) {
                        ui.showModal(components.createUserForm(user), 'Edit User');
                        this.handleUserFormSubmit(id);
                    }
                }
            });
        });

        document.querySelectorAll('.delete-user-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.dataset.id;
                if (confirm('Are you sure you want to delete this user?')) {
                    const response = await api.deleteUser(id);
                    if (response.success) {
                        this.showAdminPage();
                        ui.showNotification('User deleted successfully!', 'success');
                    } else {
                        ui.showNotification('Error deleting user.', 'error');
                    }
                }
            });
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

    async logout() {
        await api.logout();
        this.user = null;
        ui.renderSidebar(false);
        router.navigate('/auth');
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
