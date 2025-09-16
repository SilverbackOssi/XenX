/**
 * Main application script for XenToba frontend
 */

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

// Global state
const state = {
    currentPage: null,
    currentUser: null,
    isAuthenticated: false
};

// Pages configuration
const pages = {
    home: {
        id: 'home',
        title: 'Dashboard',
        render: renderHome
    },
    admin: {
        id: 'admin',
        title: 'Admin Panel',
        render: renderAdmin
    },
    auth: {
        id: 'auth',
        title: 'Authentication',
        render: renderAuth
    },
    enterprises: {
        id: 'enterprises',
        title: 'Enterprises',
        render: renderEnterprises
    },
    apiExplorer: {
        id: 'api-explorer',
        title: 'API Explorer',
        render: renderApiExplorer
    }
};

// Initialize the application
async function initApp() {
    // Set up event listeners for navigation
    document.getElementById('nav-home').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('home');
    });
    
    document.getElementById('nav-admin').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('admin');
    });
    
    document.getElementById('nav-auth').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('auth');
    });
    
    document.getElementById('nav-enterprises').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('enterprises');
    });
    
    document.getElementById('nav-api').addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo('apiExplorer');
    });

    // Check for authentication
    try {
        const user = await api.getCurrentUser();
        state.currentUser = user;
        state.isAuthenticated = true;
        
        // If we just authenticated through Google, show notification
        if (localStorage.getItem('google_auth_success')) {
            localStorage.removeItem('google_auth_success');
            showNotification('Successfully signed in with Google', 'success');
        }
    } catch (error) {
        state.isAuthenticated = false;
    }

    // Handle URL routing
    handleUrlRouting();

    // Add event listener for popstate (browser back/forward)
    window.addEventListener('popstate', (e) => {
        handleUrlRouting();
    });
}

// Handle URL routing
function handleUrlRouting() {
    const path = window.location.pathname;
    
    if (path === '/' || path === '') {
        navigateTo('home');
    } else if (path === '/admin') {
        navigateTo('admin');
    } else if (path === '/auth') {
        navigateTo('auth');
    } else if (path === '/enterprises') {
        navigateTo('enterprises');
    } else if (path === '/api-explorer') {
        navigateTo('apiExplorer');
    } else {
        navigateTo('home'); // Default fallback
    }
}

// Navigate to a specific page
function navigateTo(pageId) {
    if (pages[pageId]) {
        state.currentPage = pageId;
        
        // Update URL without reloading
        const url = pageId === 'home' ? '/' : `/${pageId.replace('apiExplorer', 'api-explorer')}`;
        history.pushState({}, pages[pageId].title, url);
        
        // Update active nav link
        const navLinks = document.querySelectorAll('nav a');
        navLinks.forEach(link => {
            link.classList.remove('active');
        });
        
        const navId = pageId === 'apiExplorer' ? 'nav-api' : `nav-${pageId}`;
        document.getElementById(navId).classList.add('active');
        
        // Render the page
        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = ''; // Clear current content
        
        // Set page title
        document.title = `XenToba - ${pages[pageId].title}`;
        
        // Add page header
        const pageHeader = document.createElement('h1');
        pageHeader.classList.add('section-title');
        pageHeader.textContent = pages[pageId].title;
        mainContent.appendChild(pageHeader);
        
        // Render page content
        pages[pageId].render(mainContent);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const alertBox = document.createElement('div');
    alertBox.classList.add('alert', `alert-${type}`);
    alertBox.textContent = message;
    
    const mainContent = document.getElementById('main-content');
    mainContent.insertBefore(alertBox, mainContent.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertBox.remove();
    }, 5000);
}

// Format date string
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Create form element
function createFormGroup(id, label, type = 'text', options = {}) {
    const formGroup = document.createElement('div');
    formGroup.classList.add('form-group');
    
    const labelElement = document.createElement('label');
    labelElement.setAttribute('for', id);
    labelElement.textContent = label;
    formGroup.appendChild(labelElement);
    
    let inputElement;
    
    if (type === 'select') {
        inputElement = document.createElement('select');
        
        if (options.options) {
            options.options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label;
                inputElement.appendChild(optionElement);
            });
        }
    } else if (type === 'textarea') {
        inputElement = document.createElement('textarea');
    } else {
        inputElement = document.createElement('input');
        inputElement.type = type;
    }
    
    inputElement.id = id;
    inputElement.name = id;
    
    if (options.placeholder) {
        inputElement.placeholder = options.placeholder;
    }
    
    if (options.value) {
        inputElement.value = options.value;
    }
    
    if (options.required) {
        inputElement.required = true;
    }
    
    formGroup.appendChild(inputElement);
    
    return formGroup;
}

// Create a button
function createButton(text, type = 'primary', clickHandler) {
    const button = document.createElement('button');
    button.textContent = text;
    button.classList.add('btn', `btn-${type}`);
    
    if (clickHandler) {
        button.addEventListener('click', clickHandler);
    }
    
    return button;
}

// Create a card element
function createCard(title, content, actions = []) {
    const card = document.createElement('div');
    card.classList.add('card');
    
    const cardTitle = document.createElement('h2');
    cardTitle.classList.add('card-title');
    cardTitle.textContent = title;
    card.appendChild(cardTitle);
    
    if (typeof content === 'string') {
        const cardContent = document.createElement('p');
        cardContent.textContent = content;
        card.appendChild(cardContent);
    } else if (content instanceof HTMLElement) {
        card.appendChild(content);
    }
    
    if (actions.length > 0) {
        const actionsDiv = document.createElement('div');
        actionsDiv.classList.add('card-actions');
        
        actions.forEach(action => {
            actionsDiv.appendChild(action);
        });
        
        card.appendChild(actionsDiv);
    }
    
    return card;
}

// Create a JSON viewer
function createJsonViewer(data) {
    const jsonViewer = document.createElement('pre');
    jsonViewer.classList.add('json-viewer');
    jsonViewer.textContent = JSON.stringify(data, null, 2);
    return jsonViewer;
}

// Render home page
function renderHome(container) {
    const welcome = document.createElement('div');
    welcome.classList.add('card');
    welcome.innerHTML = `
        <h2>XenToba Admin Testing Interface</h2>
        <p>This interface allows us to test all API endpoints and manage application data.</p>
        <p>Use the navigation menu to access different sections:</p>
        <ul>
            <li><strong>Admin:</strong> Manage users and administrative tasks</li>
            <li><strong>Auth:</strong> Test authentication endpoints</li>
            <li><strong>Enterprises:</strong> Manage enterprise data</li>
            <li><strong>API Explorer:</strong> Interactive API documentation and testing</li>
        </ul>
    `;
    container.appendChild(welcome);
    
    // Add quick stats/actions section
    const statsSection = document.createElement('div');
    statsSection.innerHTML = '<h2>Quick Actions</h2>';
    
    const actionsGrid = document.createElement('div');
    actionsGrid.classList.add('card-grid');
    
    // Auth Quick Action
    const authCard = createCard(
        'Authentication',
        'Test login, registration, and other auth features',
        [createButton('Go to Auth', 'primary', () => navigateTo('auth'))]
    );
    actionsGrid.appendChild(authCard);
    
    // Admin Quick Action
    const adminCard = createCard(
        'Admin Panel',
        'Access user management and other administrative features',
        [createButton('Go to Admin', 'primary', () => navigateTo('admin'))]
    );
    actionsGrid.appendChild(adminCard);
    
    // Enterprises Quick Action
    const enterprisesCard = createCard(
        'Enterprises',
        'Manage enterprise data and subscriptions',
        [createButton('Go to Enterprises', 'primary', () => navigateTo('enterprises'))]
    );
    actionsGrid.appendChild(enterprisesCard);
    
    statsSection.appendChild(actionsGrid);
    container.appendChild(statsSection);
}

// Render admin page
function renderAdmin(container) {
    // Create tabs for different admin sections
    const tabs = document.createElement('div');
    tabs.classList.add('tabs');
    
    const tabUsers = document.createElement('div');
    tabUsers.classList.add('tab', 'active');
    tabUsers.textContent = 'Users Management';
    tabUsers.addEventListener('click', () => {
        activateTab(tabUsers, 'tab-content-users');
    });
    tabs.appendChild(tabUsers);
    
    const tabSuperUsers = document.createElement('div');
    tabSuperUsers.classList.add('tab');
    tabSuperUsers.textContent = 'Superuser Creation';
    tabSuperUsers.addEventListener('click', () => {
        activateTab(tabSuperUsers, 'tab-content-superusers');
    });
    tabs.appendChild(tabSuperUsers);
    
    const tabBatchUsers = document.createElement('div');
    tabBatchUsers.classList.add('tab');
    tabBatchUsers.textContent = 'Batch User Creation';
    tabBatchUsers.addEventListener('click', () => {
        activateTab(tabBatchUsers, 'tab-content-batchusers');
    });
    tabs.appendChild(tabBatchUsers);
    
    container.appendChild(tabs);
    
    // Tab contents
    const tabContents = document.createElement('div');
    tabContents.classList.add('tab-contents');
    
    // Users Management Tab
    const usersTab = document.createElement('div');
    usersTab.classList.add('tab-content', 'active');
    usersTab.id = 'tab-content-users';
    
    // User listing
    const usersList = document.createElement('div');
    usersList.classList.add('card');
    
    const usersListHeader = document.createElement('div');
    usersListHeader.classList.add('card-header');
    usersListHeader.innerHTML = `
        <h2>Users List</h2>
        <p>Manage all users in the system</p>
    `;
    usersList.appendChild(usersListHeader);
    
    const userTable = document.createElement('table');
    userTable.innerHTML = `
        <thead>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Name</th>
                <th>Subscription</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="users-table-body">
            <tr>
                <td colspan="7" style="text-align: center;">Loading users...</td>
            </tr>
        </tbody>
    `;
    usersList.appendChild(userTable);
    
    // Create user form
    const createUserForm = document.createElement('div');
    createUserForm.classList.add('card');
    createUserForm.innerHTML = `
        <h2>Create User</h2>
        <form id="create-user-form">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="first_name">First Name</label>
                <input type="text" id="first_name" name="first_name">
            </div>
            <div class="form-group">
                <label for="last_name">Last Name</label>
                <input type="text" id="last_name" name="last_name">
            </div>
            <div class="form-group">
                <label for="phone_number">Phone Number</label>
                <input type="text" id="phone_number" name="phone_number">
            </div>
            <div class="form-group">
                <label for="is_active">Active</label>
                <select id="is_active" name="is_active">
                    <option value="true">Yes</option>
                    <option value="false">No</option>
                </select>
            </div>
            <div class="form-group">
                <label for="is_superuser">Superuser</label>
                <select id="is_superuser" name="is_superuser">
                    <option value="false" selected>No</option>
                    <option value="true">Yes</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Create User</button>
        </form>
    `;
    
    // Add form submission handler
    usersTab.appendChild(usersList);
    usersTab.appendChild(createUserForm);
    
    // Superusers Tab
    const superusersTab = document.createElement('div');
    superusersTab.classList.add('tab-content');
    superusersTab.id = 'tab-content-superusers';
    
    const superUserForm = document.createElement('div');
    superUserForm.classList.add('card');
    superUserForm.innerHTML = `
        <h2>Create Superuser</h2>
        <p>Create a new superuser with administrative privileges</p>
        <form id="create-superuser-form">
            <div class="form-group">
                <label for="super-username">Username</label>
                <input type="text" id="super-username" name="username" required>
            </div>
            <div class="form-group">
                <label for="super-email">Email</label>
                <input type="email" id="super-email" name="email" required>
            </div>
            <div class="form-group">
                <label for="super-password">Password</label>
                <input type="password" id="super-password" name="password" required>
            </div>
            <div class="form-group">
                <label for="super-first_name">First Name</label>
                <input type="text" id="super-first_name" name="first_name">
            </div>
            <div class="form-group">
                <label for="super-last_name">Last Name</label>
                <input type="text" id="super-last_name" name="last_name">
            </div>
            <button type="submit" class="btn btn-primary">Create Superuser</button>
        </form>
    `;
    
    superusersTab.appendChild(superUserForm);
    
    // Batch Users Tab
    const batchUsersTab = document.createElement('div');
    batchUsersTab.classList.add('tab-content');
    batchUsersTab.id = 'tab-content-batchusers';
    
    const batchUserForm = document.createElement('div');
    batchUserForm.classList.add('card');
    batchUserForm.innerHTML = `
        <h2>Create Multiple Users</h2>
        <p>Create multiple users at once using JSON format</p>
        <div class="form-group">
            <label for="batch-users-json">Users JSON (Array of user objects)</label>
            <textarea id="batch-users-json" rows="10" placeholder='[
  {
    "username": "user1",
    "email": "user1@example.com",
    "password": "Password123!",
    "first_name": "First",
    "last_name": "User"
  },
  {
    "username": "user2",
    "email": "user2@example.com",
    "password": "Password123!",
    "first_name": "Second",
    "last_name": "User"
  }
]'></textarea>
        </div>
        <button id="create-batch-users-btn" class="btn btn-primary">Create Users</button>
        <div id="batch-result" class="json-viewer" style="display: none;"></div>
    `;
    
    batchUsersTab.appendChild(batchUserForm);
    
    // Add all tabs to container
    tabContents.appendChild(usersTab);
    tabContents.appendChild(superusersTab);
    tabContents.appendChild(batchUsersTab);
    
    container.appendChild(tabContents);
    
    // Initialize the admin page
    initAdminPage();
}

// Initialize admin page
function initAdminPage() {
    // Load users list
    loadUsersList();
    
    // Create user form submission
    const createUserForm = document.getElementById('create-user-form');
    if (createUserForm) {
        createUserForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(createUserForm);
            const userData = {
                username: formData.get('username'),
                email: formData.get('email'),
                password: formData.get('password'),
                first_name: formData.get('first_name') || null,
                last_name: formData.get('last_name') || null,
                phone_number: formData.get('phone_number') || null,
                is_active: formData.get('is_active') === 'true',
                is_superuser: formData.get('is_superuser') === 'true',
                email_verified: false
            };
            
            try {
                const response = await api.createUser(userData);
                showNotification('User created successfully!', 'success');
                createUserForm.reset();
                loadUsersList();
            } catch (error) {
                showNotification(`Error creating user: ${error.message}`, 'danger');
            }
        });
    }
    
    // Create superuser form submission
    const createSuperUserForm = document.getElementById('create-superuser-form');
    if (createSuperUserForm) {
        createSuperUserForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(createSuperUserForm);
            const userData = {
                username: formData.get('username'),
                email: formData.get('email'),
                password: formData.get('password'),
                first_name: formData.get('first_name') || null,
                last_name: formData.get('last_name') || null
            };
            
            try {
                const response = await api.createSuperUser(userData);
                showNotification('Superuser created successfully!', 'success');
                createSuperUserForm.reset();
                loadUsersList();
            } catch (error) {
                showNotification(`Error creating superuser: ${error.message}`, 'danger');
            }
        });
    }
    
    // Batch user creation
    const createBatchUsersBtn = document.getElementById('create-batch-users-btn');
    if (createBatchUsersBtn) {
        createBatchUsersBtn.addEventListener('click', async () => {
            const jsonTextarea = document.getElementById('batch-users-json');
            const batchResult = document.getElementById('batch-result');
            
            try {
                const usersData = JSON.parse(jsonTextarea.value);
                
                try {
                    const response = await api.createBatchUsers(usersData);
                    batchResult.style.display = 'block';
                    batchResult.textContent = JSON.stringify(response, null, 2);
                    showNotification(`Created ${response.length} users successfully!`, 'success');
                    loadUsersList();
                } catch (error) {
                    showNotification(`Error creating users: ${error.message}`, 'danger');
                }
            } catch (jsonError) {
                showNotification('Invalid JSON format', 'danger');
            }
        });
    }
}

// Load users list
async function loadUsersList() {
    const tableBody = document.getElementById('users-table-body');
    if (!tableBody) return;
    
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Loading users...</td></tr>';
    
    try {
        const users = await api.getAllUsers();
        
        if (users.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No users found</td></tr>';
            return;
        }
        
        tableBody.innerHTML = '';
        
        users.forEach(user => {
            const tr = document.createElement('tr');
            
            tr.innerHTML = `
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${user.first_name || ''} ${user.last_name || ''}</td>
                <td>${user.subscription_plan}</td>
                <td>${user.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                    <button class="btn btn-sm" data-action="view" data-id="${user.id}">View</button>
                    <button class="btn btn-sm btn-secondary" data-action="edit" data-id="${user.id}">Edit</button>
                    <button class="btn btn-sm btn-danger" data-action="delete" data-id="${user.id}">Delete</button>
                </td>
            `;
            
            // Add event listeners for buttons
            const viewBtn = tr.querySelector('[data-action="view"]');
            const editBtn = tr.querySelector('[data-action="edit"]');
            const deleteBtn = tr.querySelector('[data-action="delete"]');
            
            viewBtn.addEventListener('click', () => viewUser(user.id));
            editBtn.addEventListener('click', () => editUser(user.id));
            deleteBtn.addEventListener('click', () => deleteUser(user.id));
            
            tableBody.appendChild(tr);
        });
    } catch (error) {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center;">Error loading users: ${error.message}</td></tr>`;
    }
}

// View user details
async function viewUser(userId) {
    try {
        const user = await api.getUserById(userId);
        
        const dialog = document.createElement('div');
        dialog.classList.add('modal-dialog');
        dialog.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>User Details</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <pre class="json-viewer">${JSON.stringify(user, null, 2)}</pre>
                </div>
                <div class="modal-footer">
                    <button class="btn">Close</button>
                </div>
            </div>
        `;
        
        // We'll use a simple approach for now - show the user data in a notification
        showNotification('User details shown in console', 'info');
        console.log('User details:', user);
        
        // In a real implementation, you would show a modal with user details
    } catch (error) {
        showNotification(`Error fetching user: ${error.message}`, 'danger');
    }
}

// Edit user
async function editUser(userId) {
    try {
        const user = await api.getUserById(userId);
        
        // Create a modal or form to edit user
        // For now, we'll use a simple approach
        
        const newUsername = prompt('New username:', user.username);
        if (!newUsername) return;
        
        const newEmail = prompt('New email:', user.email);
        if (!newEmail) return;
        
        const updatedData = {
            username: newUsername,
            email: newEmail
        };
        
        try {
            await api.updateUser(userId, updatedData);
            showNotification('User updated successfully', 'success');
            loadUsersList();
        } catch (error) {
            showNotification(`Error updating user: ${error.message}`, 'danger');
        }
        
    } catch (error) {
        showNotification(`Error fetching user: ${error.message}`, 'danger');
    }
}

// Delete user
async function deleteUser(userId) {
    if (!confirm(`Are you sure you want to delete user with ID ${userId}?`)) {
        return;
    }
    
    try {
        await api.deleteUser(userId);
        showNotification('User deleted successfully', 'success');
        loadUsersList();
    } catch (error) {
        showNotification(`Error deleting user: ${error.message}`, 'danger');
    }
}

// Activate tab
function activateTab(tabElement, contentId) {
    // Deactivate all tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Deactivate all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Activate selected tab and content
    tabElement.classList.add('active');
    document.getElementById(contentId).classList.add('active');
}

// Render auth page
function renderAuth(container) {
    const authCard = document.createElement('div');
    authCard.classList.add('card');
    
    // Create login form
    const loginForm = document.createElement('form');
    loginForm.id = 'login-form';
    loginForm.innerHTML = `
        <h2>Login</h2>
        <div class="form-group">
            <label for="login-email">Email</label>
            <input type="email" id="login-email" name="email" required>
        </div>
        <div class="form-group">
            <label for="login-password">Password</label>
            <input type="password" id="login-password" name="password" required>
        </div>
        <button type="submit" class="btn btn-primary">Login</button>
    `;
    
    // Add Google Sign-In button
    const googleSignInDiv = document.createElement('div');
    googleSignInDiv.classList.add('google-signin');
    googleSignInDiv.style.marginTop = '1rem';
    googleSignInDiv.style.textAlign = 'center';
    googleSignInDiv.innerHTML = `
        <p>- OR -</p>
        <button id="google-login-btn" class="btn" style="background-color: #fff; color: #757575; border: 1px solid #ddd; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
            <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google" style="height: 18px; margin-right: 10px;">
            Sign in with Google
        </button>
    `;
    loginForm.appendChild(googleSignInDiv);
    
    // Create register form
    const registerForm = document.createElement('form');
    registerForm.id = 'register-form';
    registerForm.style.marginTop = '2rem';
    registerForm.innerHTML = `
        <h2>Register</h2>
        <div class="form-group">
            <label for="register-email">Email</label>
            <input type="email" id="register-email" name="email" required>
        </div>
        <div class="form-group">
            <label for="register-username">Username</label>
            <input type="text" id="register-username" name="username" required>
        </div>
        <div class="form-group">
            <label for="register-password">Password</label>
            <input type="password" id="register-password" name="password" required>
        </div>
        <div class="form-group">
            <label for="register-first_name">First Name</label>
            <input type="text" id="register-first_name" name="first_name">
        </div>
        <div class="form-group">
            <label for="register-last_name">Last Name</label>
            <input type="text" id="register-last_name" name="last_name">
        </div>
        <button type="submit" class="btn btn-primary">Register</button>
    `;
    
    authCard.appendChild(loginForm);
    authCard.appendChild(registerForm);
    
    container.appendChild(authCard);
    
    // User profile section (shown when logged in)
    const profileSection = document.createElement('div');
    profileSection.id = 'user-profile';
    profileSection.style.display = state.isAuthenticated ? 'block' : 'none';
    profileSection.innerHTML = `
        <div class="card">
            <h2>User Profile</h2>
            <div id="profile-data"></div>
            <button id="logout-btn" class="btn btn-danger">Logout</button>
        </div>
    `;
    
    container.appendChild(profileSection);
    
    // Initialize auth page
    initAuthPage();
}

// Initialize auth page
function initAuthPage() {
    // Login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            
            try {
                const response = await api.login(email, password);
                state.currentUser = await api.getCurrentUser();
                state.isAuthenticated = true;
                
                // Update UI to show profile
                document.getElementById('user-profile').style.display = 'block';
                updateProfileData();
                
                showNotification('Logged in successfully', 'success');
            } catch (error) {
                showNotification(`Login failed: ${error.message}`, 'danger');
            }
        });
    }
    
    // Google login button
    const googleLoginBtn = document.getElementById('google-login-btn');
    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', () => {
            window.location.href = api.getGoogleLoginUrl();
        });
    }
    
    // Check for Google OAuth callback
    const urlParams = window.location.search;
    if (urlParams.includes('access_token')) {
        const result = api.processGoogleCallback(urlParams);
        
        if (result.success) {
            (async () => {
                try {
                    state.currentUser = await api.getCurrentUser();
                    state.isAuthenticated = true;
                    
                    // Update UI to show profile
                    const userProfile = document.getElementById('user-profile');
                    if (userProfile) {
                        userProfile.style.display = 'block';
                        updateProfileData();
                    }
                    
                    showNotification('Google login successful', 'success');
                    
                    // Clear the tokens from URL
                    history.replaceState({}, document.title, window.location.pathname);
                } catch (error) {
                    showNotification(`Error retrieving user profile: ${error.message}`, 'danger');
                }
            })();
        }
    }
    
    // Register form submission
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(registerForm);
            const userData = {
                email: formData.get('email'),
                username: formData.get('username'),
                password: formData.get('password'),
                first_name: formData.get('first_name') || null,
                last_name: formData.get('last_name') || null
            };
            
            try {
                const response = await api.register(userData);
                showNotification('Registration successful! You can now log in.', 'success');
                registerForm.reset();
            } catch (error) {
                showNotification(`Registration failed: ${error.message}`, 'danger');
            }
        });
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await api.logout();
                state.currentUser = null;
                state.isAuthenticated = false;
                
                // Update UI to hide profile
                document.getElementById('user-profile').style.display = 'none';
                
                showNotification('Logged out successfully', 'success');
            } catch (error) {
                showNotification(`Logout failed: ${error.message}`, 'danger');
            }
        });
    }
    
    // Update profile data if authenticated
    if (state.isAuthenticated) {
        updateProfileData();
    }
}

// Update profile data
function updateProfileData() {
    const profileData = document.getElementById('profile-data');
    if (!profileData || !state.currentUser) return;
    
    profileData.innerHTML = `
        <div class="json-viewer">
            ${JSON.stringify(state.currentUser, null, 2)}
        </div>
    `;
}

// Render enterprises page
function renderEnterprises(container) {
    const enterprisesCard = document.createElement('div');
    enterprisesCard.classList.add('card');
    enterprisesCard.innerHTML = `
        <h2>Enterprise Management</h2>
        <p>Manage enterprises and their subscriptions</p>
        <div id="enterprises-list">
            <p>Loading enterprises...</p>
        </div>
    `;
    
    // Create enterprise form
    const createEnterpriseForm = document.createElement('div');
    createEnterpriseForm.classList.add('card');
    createEnterpriseForm.innerHTML = `
        <h2>Create Enterprise</h2>
        <form id="create-enterprise-form">
            <div class="form-group">
                <label for="enterprise-name">Name</label>
                <input type="text" id="enterprise-name" name="name" required>
            </div>
            <div class="form-group">
                <label for="enterprise-description">Description</label>
                <textarea id="enterprise-description" name="description"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Create Enterprise</button>
        </form>
    `;
    
    container.appendChild(enterprisesCard);
    container.appendChild(createEnterpriseForm);
    
    // Initialize enterprises page
    loadEnterprises();
}

// Load enterprises
async function loadEnterprises() {
    const enterprisesList = document.getElementById('enterprises-list');
    if (!enterprisesList) return;
    
    try {
        const enterprises = await api.getAllEnterprises();
        
        if (enterprises.length === 0) {
            enterprisesList.innerHTML = '<p>No enterprises found</p>';
            return;
        }
        
        let html = '<table><thead><tr><th>ID</th><th>Name</th><th>Description</th><th>Actions</th></tr></thead><tbody>';
        
        enterprises.forEach(enterprise => {
            html += `
                <tr>
                    <td>${enterprise.id}</td>
                    <td>${enterprise.name}</td>
                    <td>${enterprise.description || '-'}</td>
                    <td>
                        <button class="btn btn-sm" onclick="viewEnterprise(${enterprise.id})">View</button>
                        <button class="btn btn-sm btn-secondary" onclick="editEnterprise(${enterprise.id})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteEnterprise(${enterprise.id})">Delete</button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        enterprisesList.innerHTML = html;
        
    } catch (error) {
        enterprisesList.innerHTML = `<p>Error loading enterprises: ${error.message}</p>`;
    }
}

// Render API explorer page
// function renderApiExplorer(container) {
//     // Create the main layout for the API explorer
//     const explorerLayout = document.createElement('div');
//     explorerLayout.classList.add('api-explorer-layout');

//     const sidebar = document.createElement('div');
//     sidebar.id = 'api-explorer-sidebar';
//     sidebar.classList.add('api-explorer-sidebar');

//     const content = document.createElement('div');
//     content.classList.add('api-explorer-content');

//     explorerLayout.appendChild(sidebar);
//     explorerLayout.appendChild(content);
//     container.appendChild(explorerLayout);

//     // Original API Explorer content
//     const apiTester = document.createElement('div');
//     apiTester.classList.add('card');
//     apiTester.innerHTML = `
//         <h2>API Request Tester</h2>
//         <form id="api-request-form">
//             <div class="form-group">
//                 <label for="api-endpoint">Endpoint</label>
//                 <input type="text" id="api-endpoint" name="api-endpoint" placeholder="/user/me">
//             </div>
//             <div class="form-group">
//                 <label for="api-method">Method</label>
//                 <select id="api-method" name="api-method">
//                     <option value="GET">GET</option>
//                     <option value="POST">POST</option>
//                     <option value="PUT">PUT</option>
//                     <option value="DELETE">DELETE</option>
//                 </select>
//             </div>
//             <div class="form-group">
//                 <label for="api-body">Request Body (JSON)</label>
//                 <textarea id="api-body" name="api-body" rows="10" placeholder='{"key": "value"}'></textarea>
//             </div>
//             <button type="submit" class="btn btn-primary">Send Request</button>
//         </form>
//     `;
//     content.appendChild(apiTester);

//     const responseContainer = document.createElement('div');
//     responseContainer.classList.add('card');
//     responseContainer.innerHTML = `
//         <h2>API Response</h2>
//         <pre id="api-response" class="json-viewer">{}</pre>
//     `;
//     content.appendChild(responseContainer);

//     // Add form submission handler
//     const apiForm = document.getElementById('api-request-form');
//     apiForm.addEventListener('submit', async (e) => {
//         e.preventDefault();
        
//         const endpoint = document.getElementById('api-endpoint').value;
//         const method = document.getElementById('api-method').value;
//         const body = document.getElementById('api-body').value;
        
//         const responsePre = document.getElementById('api-response');
//         responsePre.textContent = 'Loading...';
        
//         try {
//             let data = null;
//             if (body.trim() !== '') {
//                 try {
//                     data = JSON.parse(body);
//                 } catch (err) {
//                     throw new Error('Invalid JSON in request body');
//                 }
//             }
            
//             const response = await api.request(endpoint, method, data);
//             responsePre.textContent = JSON.stringify(response, null, 2);
//         } catch (error) {
//             const errorResponse = {
//                 error: true,
//                 status: error.status,
//                 message: error.message,
//                 data: error.data
//             };
//             responsePre.textContent = JSON.stringify(errorResponse, null, 2);
//         }
//     });

//     // Fetch and populate sidebar
//     populateApiSidebar(sidebar);
// }


async function populateApiSidebar(sidebar) {
    sidebar.innerHTML = '<h2>Available Endpoints</h2>';
    const endpointList = document.createElement('ul');
    endpointList.classList.add('endpoint-list');
    sidebar.appendChild(endpointList);

    try {
        const schema = await api.getOpenAPISchema();
        const paths = schema.paths;

        for (const path in paths) {
            for (const method in paths[path]) {
                const endpoint = paths[path][method];
                const listItem = document.createElement('li');
                
                const methodSpan = document.createElement('span');
                methodSpan.classList.add('method', method.toUpperCase());
                methodSpan.textContent = method.toUpperCase();
                
                const pathSpan = document.createElement('span');
                pathSpan.classList.add('path');
                pathSpan.textContent = path;

                listItem.appendChild(methodSpan);
                listItem.appendChild(pathSpan);

                listItem.dataset.path = path;
                listItem.dataset.method = method;
                
                // Add request body to dataset if it exists
                if (endpoint.requestBody && endpoint.requestBody.content && endpoint.requestBody.content['application/json']) {
                    const schemaRef = endpoint.requestBody.content['application/json'].schema.$ref;
                    if (schemaRef) {
                        const schemaName = schemaRef.split('/').pop();
                        const componentSchema = schema.components.schemas[schemaName];
                        if (componentSchema && componentSchema.properties) {
                            const exampleBody = {};
                            for (const prop in componentSchema.properties) {
                                const propDetails = componentSchema.properties[prop];
                                exampleBody[prop] = propDetails.example || (propDetails.type === 'integer' ? 0 : (propDetails.type === 'boolean' ? false : ''));
                            }
                            listItem.dataset.body = JSON.stringify(exampleBody, null, 2);
                        }
                    }
                }

                endpointList.appendChild(listItem);
            }
        }

        // Add click event listener to the list
        endpointList.addEventListener('click', (e) => {
            const listItem = e.target.closest('li');
            if (!listItem) return;

            const path = listItem.dataset.path;
            const method = listItem.dataset.method;
            const body = listItem.dataset.body || '';

            document.getElementById('api-endpoint').value = path;
            document.getElementById('api-method').value = method.toUpperCase();
            document.getElementById('api-body').value = body;
        });

    } catch (error) {
        console.error('Failed to load API endpoints:', error);
        endpointList.innerHTML = '<li>Failed to load endpoints.</li>';
    }
}
