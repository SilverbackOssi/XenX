// Manages UI updates and component rendering
const ui = {
    sidebar: document.getElementById('sidebar'),
    mainContent: document.getElementById('main-content'),
    menuToggle: document.getElementById('menu-toggle'),

    init() {
        this.menuToggle.addEventListener('click', () => this.sidebar.classList.toggle('open'));
    },

    async renderSidebar(isLoggedIn) {
        const navLinks = isLoggedIn
            ? `
                <a href="/"><i class="material-icons">dashboard</i><span>Dashboard</span></a>
                <a href="/profile"><i class="material-icons">person</i><span>Profile</span></a>
                <a href="/enterprises"><i class="material-icons">business</i><span>Enterprises</span></a>
                <a href="/tax-planner"><i class="material-icons">calculate</i><span>Tax Planner</span></a>
                <a href="/api-explorer"><i class="material-icons">api</i><span>API Explorer</span></a>
                <a href="/admin"><i class="material-icons">admin_panel_settings</i><span>Admin</span></a>
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
                const currentUserResponse = await api.getCurrentUser();
                const allUsersResponse = await api.getAllUsersForTesting();
                
                if (currentUserResponse.success && allUsersResponse.success) {
                    userSwitcherContent = components.createUserSwitcher(
                        allUsersResponse.data, 
                        currentUserResponse.data.id
                    );
                }
            } catch (error) {
                console.error('Failed to load user switcher:', error);
            }
        }

        this.sidebar.innerHTML = `
            <h3>XenToba</h3>
            <nav>${navLinks}</nav>
            ${userSwitcherContent}
        `;

        if (isLoggedIn) {
            document.getElementById('logout-btn').addEventListener('click', () => app.logout());
            this.attachUserSwitcherListeners();
        }
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

                // Try default password first
                const defaultPassword = userEmail.includes('admin') ? 'Admin@123' : 'Password@123';
                
                try {
                    const loginResponse = await api.login(userEmail, defaultPassword);
                    if (loginResponse.success) {
                        // Success! Reload the page to switch user
                        ui.showNotification(`Switched to ${userEmail}`, 'success');
                        window.location.reload();
                        return;
                    }
                } catch (error) {
                    console.log('Default password failed, prompting user');
                }

                // Default password failed, show password prompt
                this.showPasswordPrompt(userEmail, username);
                
                // Reset dropdown to current user
                e.target.value = '';
            });
        }
    },

    showPasswordPrompt(userEmail, username) {
        const modalContent = components.createPasswordPromptModal(userEmail);
        this.showModal(modalContent, 'Authentication Required');
        
        const form = document.getElementById('password-prompt-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('switch-password').value;
            
            try {
                const loginResponse = await api.login(userEmail, password);
                if (loginResponse.success) {
                    this.closeModal();
                    ui.showNotification(`Switched to ${userEmail}`, 'success');
                    window.location.reload();
                } else {
                    ui.showNotification('Invalid password', 'error');
                }
            } catch (error) {
                ui.showNotification('Login failed', 'error');
            }
        });
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

