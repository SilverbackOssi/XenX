// Reusable UI components
const components = {
    createAuthContainer(initialView = 'login') {
        const loginForm = `
            <form id="login-form">
                <h2>Login</h2>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
                <button type="button" id="google-login-btn" class="google-btn">Login with Google</button>
                <p class="auth-toggle" data-view="register">Don't have an account? Register</p>
            </form>
        `;

        const registerForm = `
            <form id="register-form">
                <h2>Register</h2>
                <input type="text" name="first_name" placeholder="First Name" required>
                <input type="text" name="last_name" placeholder="Last Name" required>
                <input type="text" name="username" placeholder="Username" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Register</button>
                <p class="auth-toggle" data-view="login">Already have an account? Login</p>
            </form>
        `;

        return `
            <div class="auth-container">
                ${initialView === 'login' ? loginForm : registerForm}
            </div>
        `;
    },

    createEnterpriseList(enterprises) {
        if (!enterprises || enterprises.length === 0) {
            return `
                <div class="card">
                    <div class="card-header">
                        <h2><i class="fas fa-building"></i> My Enterprises</h2>
                        <button class="btn btn-primary" id="add-enterprise-btn">
                            <i class="fas fa-plus"></i> Create New Enterprise
                        </button>
                    </div>
                    <div class="empty-state">
                        <i class="fas fa-building" style="font-size: 3rem; color: #ccc; margin-bottom: 1rem;"></i>
                        <h3>No Enterprises Found</h3>
                        <p>You haven't created any enterprises yet. Click the button above to get started!</p>
                    </div>
                </div>
            `;
        }

        const enterpriseCards = enterprises.map(enterprise => `
            <div class="enterprise-card">
                <div class="enterprise-header">
                    <div class="enterprise-info">
                        <h3>${enterprise.name}</h3>
                        <p class="enterprise-type">${enterprise.type.replace(/_/g, ' ')}</p>
                        <p class="enterprise-location">${enterprise.city}, ${enterprise.country}</p>
                    </div>
                    <div class="enterprise-status ${enterprise.is_active ? 'active' : 'inactive'}">
                        ${enterprise.is_active ? 'Active' : 'Inactive'}
                    </div>
                </div>
                <div class="enterprise-details">
                    <p><strong>Email:</strong> ${enterprise.email}</p>
                    <p><strong>Tax Year:</strong> ${enterprise.tax_year}</p>
                    ${enterprise.description ? `<p><strong>Description:</strong> ${enterprise.description}</p>` : ''}
                    ${enterprise.website ? `<p><strong>Website:</strong> <a href="${enterprise.website}" target="_blank">${enterprise.website}</a></p>` : ''}
                    <div class="enterprise-stats">
                        <span class="stat">
                            <i class="fas fa-users"></i> ${enterprise.staff_ids.length} Staff
                        </span>
                        <span class="stat">
                            <i class="fas fa-user-friends"></i> ${enterprise.client_ids.length} Clients
                        </span>
                    </div>
                </div>
                <div class="enterprise-actions">
                    <button class="btn btn-secondary view-btn" data-id="${enterprise.id}">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-primary edit-btn" data-id="${enterprise.id}">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger delete-btn" data-id="${enterprise.id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');

        return `
            <div class="card">
                <div class="card-header">
                    <h2><i class="fas fa-building"></i> My Enterprises</h2>
                    <button class="btn btn-primary" id="add-enterprise-btn">
                        <i class="fas fa-plus"></i> Create New Enterprise
                    </button>
                </div>
                <div class="enterprises-grid">
                    ${enterpriseCards}
                </div>
            </div>
        `;
    },

    createEnterpriseForm(enterprise = {}) {
        const enterpriseTypes = [
            { value: 'accounting', label: 'Accounting' },
            { value: 'tax-advisory', label: 'Tax Advisory' },
            { value: 'consulting', label: 'Consulting' }, 
            { value: 'bookkeeping', label: 'Bookkeeping' },
            { value: 'other', label: 'Other' }
        ];

        const typeOptions = enterpriseTypes.map(type => 
            `<option value="${type.value}" ${enterprise.type === type.value ? 'selected' : ''}>
                ${type.label}
            </option>`
        ).join('');

        const currentYear = new Date().getFullYear();
        const taxYear = enterprise.tax_year || currentYear;

        return `
            <form id="enterprise-form">
                <div class="form-group">
                    <label for="name">Enterprise Name *</label>
                    <input type="text" id="name" name="name" placeholder="Enter enterprise name" 
                           value="${enterprise.name || ''}" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Enterprise Email *</label>
                    <input type="email" id="email" name="email" placeholder="Enter enterprise email" 
                           value="${enterprise.email || ''}" required>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="type">Type *</label>
                        <select id="type" name="type" required>
                            <option value="">Select Type</option>
                            ${typeOptions}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="tax_year">Tax Year *</label>
                        <input type="number" id="tax_year" name="tax_year" 
                               value="${taxYear}" min="2020" max="2030" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="country">Country *</label>
                        <input type="text" id="country" name="country" placeholder="Enter country" 
                               value="${enterprise.country || ''}" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="city">City *</label>
                        <input type="text" id="city" name="city" placeholder="Enter city" 
                               value="${enterprise.city || ''}" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="address">Address</label>
                    <input type="text" id="address" name="address" placeholder="Enter address" 
                           value="${enterprise.address || ''}">
                </div>
                
                <div class="form-group">
                    <label for="website">Website</label>
                    <input type="url" id="website" name="website" placeholder="https://example.com" 
                           value="${enterprise.website || ''}">
                </div>
                
                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" name="description" rows="4" 
                              placeholder="Enter enterprise description">${enterprise.description || ''}</textarea>
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> ${enterprise.id ? 'Update' : 'Create'} Enterprise
                    </button>
                </div>
            </form>
        `;
    },

    createTaxPlannerDashboard(projects) {
        const projectCards = projects.map(project => `
            <div class="project-card">
                <h3>${project.name}</h3>
                <p>${project.description}</p>
                <p><strong>Year:</strong> ${project.year}</p>
                <div class="actions">
                    <a data-id="${project.id}" class="view-btn">View</a>
                    <a data-id="${project.id}" class="edit-project-btn">Edit</a>
                    <a data-id="${project.id}" class="delete-project-btn">Delete</a>
                </div>
            </div>
        `).join('');

        return `
            <div class="card">
                <div class="card-header">
                    <h2>Tax Planner</h2>
                    <button class="btn" id="add-project-btn">Add Project</button>
                </div>
                <div class="tax-planner-grid">
                    ${projectCards}
                </div>
            </div>
        `;
    },

    createTaxProjectForm(project = {}) {
        return `
            <form id="tax-project-form">
                <input type="text" name="name" placeholder="Project Name" value="${project.name || ''}" required>
                <input type="number" name="year" placeholder="Tax Year" value="${project.year || new Date().getFullYear()}" required>
                <textarea name="description" placeholder="Project Description">${project.description || ''}</textarea>
                <button type="submit" class="btn">${project.id ? 'Update' : 'Create'} Project</button>
            </form>
        `;
    },

    createAdminDashboard(users, stats) {
        const statsCards = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>${stats.total_users || users.length}</h3>
                    <p>Total Users</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_enterprises || 0}</h3>
                    <p>Total Enterprises</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_projects || 0}</h3>
                    <p>Tax Projects</p>
                </div>
            </div>
        `;

        const userTableRows = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.full_name}</td>
                <td>${user.email}</td>
                <td>${user.is_active ? 'Active' : 'Inactive'}</td>
                <td>${user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</td>
                <td class="actions">
                    <a data-id="${user.id}" class="edit-user-btn">Edit</a>
                    <a data-id="${user.id}" class="delete-user-btn">Delete</a>
                </td>
            </tr>
        `).join('');

        return `
            <div class="admin-dashboard">
                <h2>Admin Dashboard</h2>
                ${statsCards}
                
                <div class="card">
                    <div class="card-header">
                        <h3>User Management</h3>
                        <button class="btn" id="add-user-btn">Add User</button>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${userTableRows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    },

    createUserForm(user = {}) {
        return `
            <form id="user-form">
                <input type="text" name="full_name" placeholder="Full Name" value="${user.full_name || ''}" required>
                <input type="email" name="email" placeholder="Email" value="${user.email || ''}" required>
                ${!user.id ? '<input type="password" name="password" placeholder="Password" required>' : ''}
                <label>
                    <input type="checkbox" name="is_active" ${user.is_active !== false ? 'checked' : ''}> 
                    Active User
                </label>
                <button type="submit" class="btn">${user.id ? 'Update' : 'Create'} User</button>
            </form>
        `;
    },

    createProfilePage(profileData) {
        const { 
            first_name, last_name, username, email, phone_number, 
            subscription_plan, is_superuser, created_at, last_login,
            owned_enterprises, staff_enterprises 
        } = profileData;

        const fullName = [first_name, last_name].filter(n => n).join(' ') || 'Not specified';
        const formatDate = (dateStr) => dateStr ? new Date(dateStr).toLocaleDateString() : 'Never';

        const ownedEnterprisesSection = owned_enterprises && owned_enterprises.length > 0 ? `
            <div class="profile-section">
                <h3><i class="fas fa-building"></i> Owned Enterprises</h3>
                <div class="enterprises-grid">
                    ${owned_enterprises.map(enterprise => `
                        <div class="enterprise-card owned" data-enterprise-id="${enterprise.id}">
                            <div class="enterprise-header">
                                <div class="enterprise-info">
                                    <h4>${enterprise.name}</h4>
                                    <p class="enterprise-type">${enterprise.type.replace(/_/g, ' ')}</p>
                                </div>
                                <div class="enterprise-actions">
                                    <button class="btn btn-sm btn-outline view-enterprise-btn" data-id="${enterprise.id}">
                                        <i class="fas fa-eye"></i> View Details
                                    </button>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : '';

        const staffEnterprisesSection = staff_enterprises && staff_enterprises.length > 0 ? `
            <div class="profile-section">
                <h3><i class="fas fa-user-tie"></i> Staff Positions</h3>
                <div class="enterprises-grid">
                    ${staff_enterprises.map(enterprise => `
                        <div class="enterprise-card staff" data-enterprise-id="${enterprise.id}">
                            <div class="enterprise-header">
                                <div class="enterprise-info">
                                    <h4>${enterprise.name}</h4>
                                    <p class="enterprise-type">${enterprise.type.replace(/_/g, ' ')}</p>
                                    <p class="staff-role"><strong>Role:</strong> <span class="role-badge">${enterprise.role}</span></p>
                                </div>
                                <div class="enterprise-actions">
                                    <button class="btn btn-sm btn-outline view-enterprise-btn" data-id="${enterprise.id}">
                                        <i class="fas fa-eye"></i> View Details
                                    </button>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : '';

        return `
            <div class="profile-container">
                <div class="profile-header">
                    <div class="profile-avatar">
                        <i class="fas fa-user-circle"></i>
                    </div>
                    <div class="profile-basic-info">
                        <h1>${fullName}</h1>
                        <p class="username">@${username}</p>
                        <p class="email">${email}</p>
                        ${is_superuser ? '<span class="admin-badge">Administrator</span>' : ''}
                    </div>
                </div>

                <div class="profile-section">
                    <h3><i class="fas fa-user"></i> Personal Information</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Full Name:</label>
                            <span>${fullName}</span>
                        </div>
                        <div class="info-item">
                            <label>Username:</label>
                            <span>${username}</span>
                        </div>
                        <div class="info-item">
                            <label>Email:</label>
                            <span>${email}</span>
                        </div>
                        <div class="info-item">
                            <label>Phone:</label>
                            <span>${phone_number || 'Not specified'}</span>
                        </div>
                        <div class="info-item">
                            <label>Subscription:</label>
                            <span class="subscription-badge ${subscription_plan.toLowerCase()}">${subscription_plan}</span>
                        </div>
                        <div class="info-item">
                            <label>Member Since:</label>
                            <span>${formatDate(created_at)}</span>
                        </div>
                        <div class="info-item">
                            <label>Last Login:</label>
                            <span>${formatDate(last_login)}</span>
                        </div>
                    </div>
                </div>

                ${ownedEnterprisesSection}
                ${staffEnterprisesSection}

                <div class="profile-actions">
                    <button class="btn btn-primary" onclick="app.showEditProfile()">
                        <i class="fas fa-edit"></i> Edit Profile
                    </button>
                    <button class="btn btn-secondary" onclick="app.showChangePassword()">
                        <i class="fas fa-key"></i> Change Password
                    </button>
                </div>
            </div>
        `;
    },

    createUserSwitcher(users, currentUserId) {
        const userOptions = users.map(user => {
            const displayName = `${user.first_name} ${user.last_name}`.trim() || user.username;
            const isCurrentUser = user.id === currentUserId;
            return `
                <option value="${user.id}" data-email="${user.email}" data-username="${user.username}" 
                        ${isCurrentUser ? 'selected' : ''}>
                    ${displayName} (${user.email})${isCurrentUser ? ' - Current' : ''}
                </option>
            `;
        }).join('');

        return `
            <div class="user-switcher">
                <label for="user-select">
                    <i class="fas fa-user-friends"></i> Switch User (Testing)
                </label>
                <select id="user-select" class="user-select">
                    <option value="">Select a user...</option>
                    ${userOptions}
                </select>
            </div>
        `;
    },

    createPasswordPromptModal(userEmail) {
        return `
            <div class="password-prompt-modal">
                <h3><i class="fas fa-key"></i> Password Required</h3>
                <p>Please enter the password for <strong>${userEmail}</strong>:</p>
                <form id="password-prompt-form">
                    <div class="form-group">
                        <input type="password" id="switch-password" name="password" 
                               placeholder="Enter password" required>
                        <small class="form-hint">
                            Try: <code>Password@123</code> for regular users or <code>Admin@123</code> for admin
                        </small>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Switch User</button>
                    </div>
                </form>
            </div>
        `;
    },

    createApiExplorer() {
        return `
            <div class="api-explorer">
                <div class="api-explorer-header">
                    <h1><i class="material-icons">api</i> API Explorer</h1>
                    <p>Test and explore all backend endpoints interactively</p>
                </div>

                <div class="api-explorer-layout">
                    <!-- Left Panel: Request Builder -->
                    <div class="api-request-panel">
                        <div class="card">
                            <div class="card-header">
                                <h3><i class="material-icons">send</i> Request Builder</h3>
                            </div>
                            <div class="card-body">
                                <!-- Quick Examples -->
                                <div class="quick-examples">
                                    <h4>Quick Examples</h4>
                                    <div class="example-buttons">
                                        <button class="btn btn-sm btn-outline example-btn" data-example="health">Health Check</button>
                                        <button class="btn btn-sm btn-outline example-btn" data-example="login">Login</button>
                                        <button class="btn btn-sm btn-outline example-btn" data-example="register">Register</button>
                                        <button class="btn btn-sm btn-outline example-btn" data-example="enterprises">Get Enterprises</button>
                                        <button class="btn btn-sm btn-outline example-btn" data-example="users">Get Users</button>
                                    </div>
                                </div>

                                <!-- Request Configuration -->
                                <div class="request-config">
                                    <div class="form-row">
                                        <div class="form-group">
                                            <label for="http-method">HTTP Method</label>
                                            <select id="http-method" class="form-control">
                                                <option value="GET">GET</option>
                                                <option value="POST">POST</option>
                                                <option value="PUT">PUT</option>
                                                <option value="PATCH">PATCH</option>
                                                <option value="DELETE">DELETE</option>
                                            </select>
                                        </div>
                                        <div class="form-group endpoint-group">
                                            <label for="endpoint-path">Endpoint</label>
                                            <div class="endpoint-input">
                                                <span class="base-url">/api/v1</span>
                                                <input type="text" id="endpoint-path" class="form-control" placeholder="/health" value="/health">
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Authentication -->
                                    <div class="form-group">
                                        <label>
                                            <input type="checkbox" id="use-auth" checked> 
                                            Use Authentication Token
                                        </label>
                                        <div id="auth-token-group" class="auth-token-group">
                                            <input type="text" id="auth-token" class="form-control" 
                                                   placeholder="JWT token (leave empty to use current session)">
                                            <small class="form-hint">Leave empty to use current session token automatically</small>
                                        </div>
                                    </div>

                                    <!-- Headers -->
                                    <div class="form-group">
                                        <label for="request-headers">Headers</label>
                                        <textarea id="request-headers" class="form-control code-editor" rows="4" 
                                                  placeholder='{"Content-Type": "application/json"}'></textarea>
                                        <small class="form-hint">JSON format. Content-Type and Authorization headers are added automatically.</small>
                                    </div>

                                    <!-- Query Parameters -->
                                    <div class="form-group">
                                        <label for="query-params">Query Parameters</label>
                                        <textarea id="query-params" class="form-control code-editor" rows="3" 
                                                  placeholder='{"limit": 10, "offset": 0}'></textarea>
                                        <small class="form-hint">JSON format. Will be converted to URL query string.</small>
                                    </div>

                                    <!-- Request Body -->
                                    <div class="form-group" id="request-body-group">
                                        <label for="request-body">Request Body</label>
                                        <textarea id="request-body" class="form-control code-editor" rows="8" 
                                                  placeholder='{\n  "email": "user@example.com",\n  "password": "password123"\n}'></textarea>
                                        <small class="form-hint">JSON format. Only for POST, PUT, PATCH requests.</small>
                                    </div>

                                    <!-- Send Button -->
                                    <div class="form-actions">
                                        <button id="send-request" class="btn btn-primary">
                                            <i class="material-icons">send</i> Send Request
                                        </button>
                                        <button id="clear-request" class="btn btn-secondary">
                                            <i class="material-icons">clear</i> Clear
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Right Panel: Response Display -->
                    <div class="api-response-panel">
                        <div class="card">
                            <div class="card-header">
                                <h3><i class="material-icons">receipt_long</i> Response</h3>
                                <div class="response-status" id="response-status">
                                    Ready to send request
                                </div>
                            </div>
                            <div class="card-body">
                                <div id="response-content" class="response-content">
                                    <div class="response-placeholder">
                                        <i class="material-icons">http</i>
                                        <p>Send a request to see the response here</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Request History -->
                        <div class="card">
                            <div class="card-header">
                                <h3><i class="material-icons">history</i> Request History</h3>
                                <button id="clear-history" class="btn btn-sm btn-secondary">
                                    <i class="material-icons">delete_sweep</i> Clear History
                                </button>
                            </div>
                            <div class="card-body">
                                <div id="request-history" class="request-history">
                                    <div class="history-placeholder">
                                        <p>Request history will appear here</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    // Add more components like tables, modals, etc. later
};
