// Manages UI updates and component rendering
const ui = {
    sidebar: document.getElementById('sidebar'),
    mainContent: document.getElementById('main-content'),
    menuToggle: document.getElementById('menu-toggle'),

    init() {
        this.menuToggle.addEventListener('click', () => this.sidebar.classList.toggle('open'));
    },

    renderSidebar(isLoggedIn) {
        const navLinks = isLoggedIn
            ? `
                <a href="/"><i class="material-icons">dashboard</i><span>Dashboard</span></a>
                <a href="/profile"><i class="material-icons">person</i><span>Profile</span></a>
                <a href="/enterprises"><i class="material-icons">business</i><span>Enterprises</span></a>
                <a href="/tax-planner"><i class="material-icons">calculate</i><span>Tax Planner</span></a>
                <a href="/admin"><i class="material-icons">admin_panel_settings</i><span>Admin</span></a>
                <button id="logout-btn"><i class="material-icons">logout</i><span>Logout</span></button>
            `
            : `
                <a href="/auth"><i class="material-icons">login</i><span>Login / Register</span></a>
            `;

        this.sidebar.innerHTML = `
            <h3>XenToba</h3>
            <nav>${navLinks}</nav>
        `;

        if (isLoggedIn) {
            document.getElementById('logout-btn').addEventListener('click', () => app.logout());
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

