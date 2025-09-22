// Manages UI updates and component rendering
const ui = {
    sidebar: document.getElementById('sidebar'),
    mainContent: document.getElementById('main-content'),
    menuToggle: document.getElementById('menu-toggle'),

    init() {
        this.menuToggle.addEventListener('click', () => this.sidebar.classList.toggle('open'));
    },

    async renderSidebar(isLoggedIn) {
        // Determine user role and permissions
        let isAdmin = false;
        let currentUser = null;
        
        if (isLoggedIn && app.user) {
            currentUser = app.user;
            isAdmin = currentUser.is_superuser || false;
        }
        
        // Create navigation links based on user role
        const navLinks = isLoggedIn
            ? `
                <a href="/"><i class="material-icons">dashboard</i><span>Dashboard</span></a>
                <a href="/profile"><i class="material-icons">person</i><span>Profile</span></a>
                <a href="/enterprises"><i class="material-icons">business</i><span>Enterprises</span></a>
                <a href="/tax-planner"><i class="material-icons">calculate</i><span>Tax Planner</span></a>
                <a href="/api-explorer"><i class="material-icons">api</i><span>API Explorer</span></a>
                ${isAdmin ? '<a href="/admin"><i class="material-icons">admin_panel_settings</i><span>Admin Panel</span></a>' : ''}
                <button id="logout-btn"><i class="material-icons">logout</i><span>Logout</span></button>
            `
            : `
                <a href="/auth"><i class="material-icons">login</i><span>Login / Register</span></a>
                <a href="/api-explorer"><i class="material-icons">api</i><span>API Explorer</span></a>
            `;

        // Get user switcher content if logged in
        let userSwitcherContent = '';
        if (isLoggedIn) {
            try {
                const allUsersResponse = await api.getAllUsersForTesting();
                
                if (allUsersResponse.success && currentUser) {
                    userSwitcherContent = components.createUserSwitcher(
                        allUsersResponse.data, 
                        currentUser.id
                    );
                } else {
                    console.warn('Failed to load user switcher data:', allUsersResponse.error);
                }
            } catch (error) {
                console.error('Failed to load user switcher:', error);
            }
        }

        // Update sidebar content
        this.sidebar.innerHTML = `
            <h3>XenToba</h3>
            <nav>${navLinks}</nav>
            ${userSwitcherContent}
        `;

        // Attach event listeners
        if (isLoggedIn) {
            const logoutBtn = document.getElementById('logout-btn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', () => app.logout());
            }
            this.attachUserSwitcherListeners();
        }
        
        console.log('🎨 Sidebar Rendered:', {
            isLoggedIn,
            isAdmin,
            currentUser: currentUser ? currentUser.email : 'none',
            switcherLoaded: !!userSwitcherContent
        });
    },

    attachUserSwitcherListeners() {
        const userSelect = document.getElementById('user-select');
        if (userSelect) {
            userSelect.addEventListener('change', async (e) => {
                const selectedUserId = e.target.value;
                if (!selectedUserId) return;

                const selectedOption = e.target.selectedOptions[0];
                const userEmail = selectedOption.dataset.email;
                const username = selectedOption.dataset.username;
                const userRole = selectedOption.dataset.role;
                const isAdmin = selectedOption.dataset.isAdmin === 'true';

                console.log('🔄 User Switch Initiated:', {
                    from: app.user?.email || 'unknown',
                    fromId: app.user?.id || null,
                    to: userEmail,
                    toId: selectedUserId,
                    role: userRole,
                    isAdmin: isAdmin,
                    availableOptions: Array.from(e.target.options).length
                });

                // Show confirmation dialog if there might be unsaved data
                const hasUnsavedData = this.checkForUnsavedData();
                if (hasUnsavedData && !await this.showSwitchUserConfirmation(userEmail, userRole, isAdmin)) {
                    // User cancelled the switch - reset dropdown
                    e.target.value = '';
                    return;
                }

                // Show switching status
                this.showSwitchUserStatus('info', 'Switching Users...', `Switching to ${userEmail}`, true);

                try {
                    // Step 1: Clear current session completely
                    await this.clearCurrentSession();
                    
                    // Step 2: Attempt login with default password
                    const defaultPassword = this.getDefaultPassword(userEmail, isAdmin);
                    const loginSuccess = await this.attemptUserLogin(userEmail, defaultPassword);
                    
                    if (loginSuccess) {
                        // Step 3: Complete the switch
                        await this.completeUserSwitch(userEmail, userRole);
                    } else {
                        // Step 4: Fallback to manual password entry
                        await this.showManualPasswordPrompt(userEmail, username, userRole);
                    }
                } catch (error) {
                    console.error('❌ User Switch Error:', error);
                    this.showSwitchUserStatus('error', 'Switch Failed', `Failed to switch to ${userEmail}: ${error.message}`, false);
                    
                    // Reset dropdown
                    e.target.value = '';
                    
                    // Try to restore previous session
                    await this.restorePreviousSession();
                }
            });
        }
    },

    checkForUnsavedData() {
        // Check for common unsaved data indicators
        const forms = document.querySelectorAll('form');
        const textareas = document.querySelectorAll('textarea');
        const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        
        // Check if any forms have been modified
        for (const form of forms) {
            const formData = new FormData(form);
            for (const [key, value] of formData.entries()) {
                if (value && value.toString().trim()) {
                    return true;
                }
            }
        }
        
        // Check for modified textareas/inputs
        for (const element of [...textareas, ...inputs]) {
            if (element.value && element.value.trim() && !element.readOnly) {
                return true;
            }
        }
        
        return false;
    },

    async showSwitchUserConfirmation(targetEmail, targetRole, isAdmin) {
        return new Promise((resolve) => {
            const displayRole = isAdmin ? 'ADMIN' : 'USER';
            const roleIcon = isAdmin ? 'admin_panel_settings' : 'person';
            
            const confirmationHtml = `
                <div class="switch-confirmation-overlay">
                    <div class="switch-confirmation-dialog">
                        <div class="switch-confirmation-header">
                            <i class="material-icons">swap_horiz</i>
                            <h3 class="switch-confirmation-title">Confirm User Switch</h3>
                        </div>
                        <div class="switch-confirmation-body">
                            <p>You are about to switch to a different user account. This will:</p>
                            <ul>
                                <li>Log out your current session completely</li>
                                <li>Clear all authentication tokens and cached data</li>
                                <li>Log you in as the selected user</li>
                                <li>Refresh all role-dependent interface elements</li>
                            </ul>
                            
                            <div class="switch-target-info">
                                <div class="switch-target-name">
                                    <i class="material-icons">${roleIcon}</i>
                                    ${targetEmail}
                                </div>
                                <div class="switch-target-meta">
                                    Role: ${displayRole} | Development Test Account
                                </div>
                            </div>
                            
                            <div class="switch-warning">
                                <i class="material-icons">warning</i>
                                <span>Any unsaved changes will be lost. This feature is for development testing only.</span>
                            </div>
                        </div>
                        <div class="switch-confirmation-actions">
                            <button class="btn btn-secondary" id="cancel-switch">Cancel</button>
                            <button class="btn btn-primary" id="confirm-switch">Switch User</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', confirmationHtml);
            const overlay = document.querySelector('.switch-confirmation-overlay');
            
            // Handle cancel
            overlay.querySelector('#cancel-switch').addEventListener('click', () => {
                overlay.remove();
                resolve(false);
            });
            
            // Handle confirm
            overlay.querySelector('#confirm-switch').addEventListener('click', () => {
                overlay.remove();
                resolve(true);
            });
            
            // Handle escape key and overlay click
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    overlay.remove();
                    document.removeEventListener('keydown', handleEscape);
                    resolve(false);
                }
            };
            
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    overlay.remove();
                    document.removeEventListener('keydown', handleEscape);
                    resolve(false);
                }
            });
            
            document.addEventListener('keydown', handleEscape);
        });
    },

    async clearCurrentSession() {
        console.log('🧹 Clearing Current Session');
        
        // Clear API tokens
        api.clearToken();
        
        // Clear localStorage completely
        const keysToPreserve = ['theme', 'language']; // Preserve user preferences
        const preservedValues = {};
        keysToPreserve.forEach(key => {
            const value = localStorage.getItem(key);
            if (value) preservedValues[key] = value;
        });
        
        localStorage.clear();
        
        // Restore preserved values
        Object.entries(preservedValues).forEach(([key, value]) => {
            localStorage.setItem(key, value);
        });
        
        // Clear sessionStorage
        sessionStorage.clear();
        
        // Clear application state
        app.user = null;
        app.currentUsers = null;
        app.currentEnterprises = null;
        
        console.log('✅ Session Cleared Successfully');
    },

    getDefaultPassword(email, isAdmin) {
        // Based on seeder script patterns
        if (email.includes('admin') || isAdmin) {
            return 'Admin@123';
        }
        return 'Password@123';
    },

    async attemptUserLogin(email, password) {
        console.log('🔐 Attempting Login:', { email, passwordLength: password.length });
        
        try {
            const response = await api.login(email, password, true); // Mark as user switch
            if (response.success && response.data?.access_token) {
                console.log('✅ Login Successful');
                // CRITICAL: Set the token for subsequent API calls
                api.setToken(response.data.access_token);
                return true;
            } else {
                console.log('❌ Login Failed:', response.error?.detail || 'Unknown error');
                return false;
            }
        } catch (error) {
            console.error('❌ Login Exception:', error);
            return false;
        }
    },

    async completeUserSwitch(email, role) {
        console.log('🎯 Completing User Switch:', { email, role });
        
        try {
            // Get current user info to verify switch
            console.log('🔍 Verifying user switch with getCurrentUser...');
            const userResponse = await api.getCurrentUser();
            console.log('👤 getCurrentUser response:', userResponse);
            
            if (!userResponse.success) {
                throw new Error('Failed to verify user switch: ' + (userResponse.error?.detail || 'Unknown error'));
            }
            
            // Update app state
            console.log('📝 Updating app state with user:', userResponse.data);
            app.user = userResponse.data;
            
            // Show success message
            this.showSwitchUserStatus('success', 'Switch Successful!', `Now logged in as ${email} (${role.toUpperCase()})`, false);
            
            // Reinitialize the application
            console.log('🔄 Reinitializing application...');
            await app.init();
            
            // Navigate to dashboard to show the new user context
            console.log('🏠 Navigating to dashboard...');
            router.navigate('/');
            
            console.log('🎉 User Switch Completed Successfully');
            
        } catch (error) {
            console.error('❌ Failed to complete user switch:', error);
            throw error;
        }
    },

    async showManualPasswordPrompt(email, username, role) {
        const modalContent = components.createPasswordPromptModal(email);
        this.showModal(modalContent, 'Authentication Required');
        
        const form = document.getElementById('password-prompt-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('switch-password').value;
            
            this.showSwitchUserStatus('info', 'Authenticating...', 'Verifying password', true);
            
            try {
                const loginSuccess = await this.attemptUserLogin(email, password);
                if (loginSuccess) {
                    this.closeModal();
                    await this.completeUserSwitch(email, role);
                } else {
                    this.showSwitchUserStatus('error', 'Authentication Failed', 'Invalid password provided', false);
                }
            } catch (error) {
                console.error('❌ Manual login error:', error);
                this.showSwitchUserStatus('error', 'Login Error', error.message, false);
            }
        });
        
        // Add cancel button handler
        const cancelBtn = document.querySelector('#password-prompt-form .btn-secondary');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.closeModal();
                this.showSwitchUserStatus('info', 'Switch Cancelled', 'User switch was cancelled', false);
            });
        }
    },

    async restorePreviousSession() {
        console.log('🔄 Attempting to restore previous session');
        
        // This is a fallback - in practice, the session is cleared so we redirect to login
        this.showSwitchUserStatus('warning', 'Session Lost', 'Please log in again', false);
        
        setTimeout(() => {
            router.navigate('/auth');
        }, 2000);
    },

    showSwitchUserStatus(type, title, message, isPersistent = false) {
        // Remove any existing status messages
        const existingStatus = document.querySelectorAll('.switch-user-status');
        existingStatus.forEach(status => status.remove());
        
        const statusContainer = document.createElement('div');
        statusContainer.className = 'switch-user-status';
        
        const iconMap = {
            'success': 'check_circle',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        };
        
        const icon = iconMap[type] || 'info';
        
        statusContainer.innerHTML = `
            <div class="switch-status-message ${type}">
                <i class="material-icons">${icon}</i>
                <div class="switch-status-content">
                    <div class="switch-status-title">${title}</div>
                    <div class="switch-status-details">${message}</div>
                </div>
                ${!isPersistent ? '<button class="switch-close-btn" onclick="this.parentElement.parentElement.remove()"><i class="material-icons">close</i></button>' : ''}
            </div>
        `;
        
        document.body.appendChild(statusContainer);
        
        // Auto-remove non-persistent messages
        if (!isPersistent) {
            setTimeout(() => {
                if (statusContainer.parentNode) {
                    statusContainer.remove();
                }
            }, type === 'error' ? 5000 : 3000);
        }
    },

    render(content) {
        this.mainContent.innerHTML = content;
        // Close sidebar on content change in mobile view
        if (window.innerWidth <= 768) {
            this.sidebar.classList.remove('open');
        }
    },

    showModal(content, title) {
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'modal-overlay';
        modalOverlay.innerHTML = `
            <div class="modal-content">
                <button class="modal-close">&times;</button>
                <h2>${title}</h2>
                ${content}
            </div>
        `;
        document.body.appendChild(modalOverlay);

        modalOverlay.querySelector('.modal-close').addEventListener('click', this.closeModal);
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                this.closeModal();
            }
        });
    },

    closeModal() {
        const modalOverlay = document.querySelector('.modal-overlay');
        if (modalOverlay) {
            modalOverlay.remove();
        }
    },

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
};

document.addEventListener('DOMContentLoaded', () => ui.init());

