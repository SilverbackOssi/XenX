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

    createAdminDashboard(users, stats, currentUser = null) {
        return `
            <div class="admin-dashboard">
                <div class="admin-header">
                    <h1><i class="material-icons">admin_panel_settings</i> Admin Dashboard</h1>
                    <p class="admin-subtitle">Developer testing interface for administrative endpoints</p>
                </div>

                <!-- Auth Debugging Panel -->
                <div class="admin-section">
                    <div class="card">
                        <div class="card-header collapsible" data-target="auth-debug">
                            <h3><i class="material-icons">verified_user</i> Authentication Debug</h3>
                            <i class="material-icons toggle-icon">expand_more</i>
                        </div>
                        <div class="card-body" id="auth-debug">
                            <div class="auth-debug-panel">
                                <div class="debug-section">
                                    <h4>Current Session</h4>
                                    <div class="debug-info">
                                        <div class="debug-item">
                                            <label>User ID:</label>
                                            <span class="copyable" data-copy="${currentUser?.id || 'Not authenticated'}">${currentUser?.id || 'Not authenticated'}</span>
                                        </div>
                                        <div class="debug-item">
                                            <label>Email:</label>
                                            <span>${currentUser?.email || 'N/A'}</span>
                                        </div>
                                        <div class="debug-item">
                                            <label>Role:</label>
                                            <span class="role-badge ${currentUser?.is_superuser ? 'superuser' : 'user'}">${currentUser?.is_superuser ? 'SUPERUSER' : 'USER'}</span>
                                        </div>
                                        <div class="debug-item">
                                            <label>Active:</label>
                                            <span class="status-badge ${currentUser?.is_active ? 'active' : 'inactive'}">${currentUser?.is_active ? 'ACTIVE' : 'INACTIVE'}</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="debug-section">
                                    <h4>JWT Token Management</h4>
                                    <div class="token-controls">
                                        <button class="btn btn-sm btn-outline" id="show-token-btn">
                                            <i class="material-icons">visibility</i> Show Token
                                        </button>
                                        <button class="btn btn-sm btn-outline" id="refresh-token-btn">
                                            <i class="material-icons">refresh</i> Refresh Session
                                        </button>
                                        <button class="btn btn-sm btn-outline" id="manual-token-btn">
                                            <i class="material-icons">edit</i> Manual Token
                                        </button>
                                    </div>
                                    <div class="token-display" id="token-display" style="display: none;">
                                        <textarea class="token-textarea" id="current-token" readonly></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- System Stats -->
                <div class="admin-section">
                    <h2>System Overview</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-icon"><i class="material-icons">people</i></div>
                            <div class="stat-content">
                                <h3>${stats.total_users || users.length}</h3>
                                <p>Total Users</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon"><i class="material-icons">business</i></div>
                            <div class="stat-content">
                                <h3>${stats.total_enterprises || 0}</h3>
                                <p>Enterprises</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon"><i class="material-icons">calculate</i></div>
                            <div class="stat-content">
                                <h3>${stats.total_projects || 0}</h3>
                                <p>Tax Projects</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon"><i class="material-icons">api</i></div>
                            <div class="stat-content">
                                <h3 id="api-calls-count">0</h3>
                                <p>API Calls (Session)</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Admin Navigation Tabs -->
                <div class="admin-tabs">
                    <button class="tab-btn active" data-tab="users">
                        <i class="material-icons">people</i> Users
                    </button>
                    <button class="tab-btn" data-tab="enterprises">
                        <i class="material-icons">business</i> Enterprises
                    </button>
                    <button class="tab-btn" data-tab="audit">
                        <i class="material-icons">history</i> Audit Log
                    </button>
                </div>

                <!-- Tab Content Areas -->
                <div class="tab-content">
                    <!-- Users Tab -->
                    <div class="tab-panel active" id="users-tab">
                        ${this.createUserManagementPanel(users)}
                    </div>

                    <!-- Enterprises Tab -->
                    <div class="tab-panel" id="enterprises-tab">
                        ${this.createEnterpriseManagementPanel([])}
                    </div>

                    <!-- Audit Log Tab -->
                    <div class="tab-panel" id="audit-tab">
                        ${this.createAuditLogPanel([])}
                    </div>
                </div>
            </div>
        `;
    },

    createUserManagementPanel(users) {
        const userTableRows = users.map(user => {
            const createdDate = user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A';
            const roleBadge = user.is_superuser ? '<span class="role-badge superuser">SUPER</span>' : '<span class="role-badge user">USER</span>';
            const statusBadge = user.is_active ? '<span class="status-badge active">ACTIVE</span>' : '<span class="status-badge inactive">INACTIVE</span>';
            
            return `
                <tr class="user-row" data-user-id="${user.id}">
                    <td>
                        <span class="copyable" data-copy="${user.id}">${user.id}</span>
                    </td>
                    <td>${user.username || user.full_name || 'N/A'}</td>
                    <td>
                        <span class="copyable" data-copy="${user.email}">${user.email}</span>
                    </td>
                    <td>${roleBadge}</td>
                    <td>${statusBadge}</td>
                    <td class="copyable" data-copy="${createdDate}">${createdDate}</td>
                    <td class="actions">
                        <button class="btn btn-sm btn-outline view-user-btn" data-id="${user.id}">
                            <i class="material-icons">visibility</i>
                        </button>
                        <button class="btn btn-sm btn-primary edit-user-btn" data-id="${user.id}">
                            <i class="material-icons">edit</i>
                        </button>
                        <button class="btn btn-sm btn-warning reset-password-btn" data-id="${user.id}">
                            <i class="material-icons">key</i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-user-btn" data-id="${user.id}">
                            <i class="material-icons">delete</i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        return `
            <div class="card">
                <div class="card-header">
                    <h3><i class="material-icons">people</i> User Management</h3>
                    <div class="header-actions">
                        <div class="search-box">
                            <input type="text" id="user-search" placeholder="Search users..." class="form-control">
                            <i class="material-icons">search</i>
                        </div>
                        <select id="user-role-filter" class="form-control">
                            <option value="">All Roles</option>
                            <option value="superuser">Superusers</option>
                            <option value="user">Regular Users</option>
                        </select>
                        <select id="user-status-filter" class="form-control">
                            <option value="">All Status</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                        <button class="btn btn-primary" id="add-user-btn">
                            <i class="material-icons">add</i> Add User
                        </button>
                        <button class="btn btn-outline" id="refresh-users-btn">
                            <i class="material-icons">refresh</i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-controls">
                        <label class="debug-toggle">
                            <input type="checkbox" id="show-user-json"> Show Raw JSON
                        </label>
                        <div class="pagination-info">
                            Showing ${users.length} users
                        </div>
                    </div>
                    
                    <div class="table-container">
                        <table class="admin-table" id="users-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Role</th>
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
                    
                    <div class="raw-json" id="users-json" style="display: none;">
                        <h4>Raw JSON Response</h4>
                        <pre class="json-viewer">${JSON.stringify(users, null, 2)}</pre>
                    </div>
                </div>
            </div>
        `;
    },

    createEnterpriseManagementPanel(enterprises) {
        const enterpriseRows = enterprises.length ? enterprises.map(enterprise => `
            <tr class="enterprise-row" data-enterprise-id="${enterprise.id}">
                <td><span class="copyable" data-copy="${enterprise.id}">${enterprise.id}</span></td>
                <td>${enterprise.name}</td>
                <td><span class="copyable" data-copy="${enterprise.slug || enterprise.id}">${enterprise.slug || 'N/A'}</span></td>
                <td>${enterprise.owner_email || enterprise.owner || 'N/A'}</td>
                <td><span class="status-badge ${enterprise.is_active ? 'active' : 'inactive'}">${enterprise.is_active ? 'ACTIVE' : 'INACTIVE'}</span></td>
                <td>${enterprise.created_at ? new Date(enterprise.created_at).toLocaleDateString() : 'N/A'}</td>
                <td class="actions">
                    <button class="btn btn-sm btn-outline view-enterprise-btn" data-id="${enterprise.id}">
                        <i class="material-icons">visibility</i>
                    </button>
                    <button class="btn btn-sm btn-primary edit-enterprise-btn" data-id="${enterprise.id}">
                        <i class="material-icons">edit</i>
                    </button>
                    <button class="btn btn-sm btn-warning manage-members-btn" data-id="${enterprise.id}">
                        <i class="material-icons">group</i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-enterprise-btn" data-id="${enterprise.id}">
                        <i class="material-icons">delete</i>
                    </button>
                </td>
            </tr>
        `).join('') : '<tr><td colspan="7" class="empty-state">No enterprises found. Click "Add Enterprise" to create one.</td></tr>';

        return `
            <div class="card">
                <div class="card-header">
                    <h3><i class="material-icons">business</i> Enterprise Management</h3>
                    <div class="header-actions">
                        <div class="search-box">
                            <input type="text" id="enterprise-search" placeholder="Search enterprises..." class="form-control">
                            <i class="material-icons">search</i>
                        </div>
                        <button class="btn btn-primary" id="add-enterprise-btn">
                            <i class="material-icons">add</i> Add Enterprise
                        </button>
                        <button class="btn btn-outline" id="refresh-enterprises-btn">
                            <i class="material-icons">refresh</i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-controls">
                        <label class="debug-toggle">
                            <input type="checkbox" id="show-enterprise-json"> Show Raw JSON
                        </label>
                        <div class="pagination-info">
                            Showing ${enterprises.length} enterprises
                        </div>
                    </div>
                    
                    <div class="table-container">
                        <table class="admin-table" id="enterprises-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Slug</th>
                                    <th>Owner</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${enterpriseRows}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="raw-json" id="enterprises-json" style="display: none;">
                        <h4>Raw JSON Response</h4>
                        <pre class="json-viewer">${JSON.stringify(enterprises, null, 2)}</pre>
                    </div>
                </div>
            </div>
        `;
    },

    createAuditLogPanel(auditLogs) {
        const logRows = auditLogs.length ? auditLogs.map((log, index) => {
            const statusClass = log.status >= 200 && log.status < 300 ? 'success' : log.status >= 400 ? 'error' : 'warning';
            const timestamp = new Date(log.timestamp).toLocaleString();
            
            return `
                <tr class="audit-row" data-log-index="${index}">
                    <td class="timestamp">${timestamp}</td>
                    <td><span class="method-badge ${log.method.toLowerCase()}">${log.method}</span></td>
                    <td class="path"><code>${log.path}</code></td>
                    <td><span class="status-badge ${statusClass}">${log.status}</span></td>
                    <td class="duration">${log.duration}ms</td>
                    <td class="actions">
                        <button class="btn btn-sm btn-outline view-request-btn" data-index="${index}">
                            <i class="material-icons">code</i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('') : '<tr><td colspan="6" class="empty-state">No API calls recorded in this session.</td></tr>';

        return `
            <div class="card">
                <div class="card-header">
                    <h3><i class="material-icons">history</i> Admin API Audit Log</h3>
                    <div class="header-actions">
                        <button class="btn btn-outline" id="clear-audit-log-btn">
                            <i class="material-icons">clear_all</i> Clear Log
                        </button>
                        <button class="btn btn-outline" id="export-audit-log-btn">
                            <i class="material-icons">download</i> Export
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="audit-stats">
                        <div class="audit-stat">
                            <span class="stat-label">Total Calls:</span>
                            <span class="stat-value">${auditLogs.length}</span>
                        </div>
                        <div class="audit-stat">
                            <span class="stat-label">Success Rate:</span>
                            <span class="stat-value">${auditLogs.length ? Math.round((auditLogs.filter(log => log.status < 400).length / auditLogs.length) * 100) : 0}%</span>
                        </div>
                        <div class="audit-stat">
                            <span class="stat-label">Avg Response Time:</span>
                            <span class="stat-value">${auditLogs.length ? Math.round(auditLogs.reduce((sum, log) => sum + log.duration, 0) / auditLogs.length) : 0}ms</span>
                        </div>
                    </div>
                    
                    <div class="table-container">
                        <table class="admin-table audit-table">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Method</th>
                                    <th>Path</th>
                                    <th>Status</th>
                                    <th>Duration</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${logRows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Request/Response Detail Panel -->
            <div class="card" id="request-detail-panel" style="display: none;">
                <div class="card-header">
                    <h3><i class="material-icons">code</i> Request/Response Details</h3>
                    <button class="btn btn-sm btn-outline" id="close-detail-panel">
                        <i class="material-icons">close</i>
                    </button>
                </div>
                <div class="card-body">
                    <div class="detail-content" id="request-detail-content">
                        <!-- Will be populated when viewing request details -->
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
        // Find current user details
        const currentUser = users.find(user => user.id === currentUserId);
        const currentUserDisplay = currentUser ? 
            `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim() || currentUser.username :
            'Unknown User';
        
        // Determine current user role
        const currentUserRole = currentUser?.is_superuser ? 'ADMIN' : 'USER';
        
        // Group users by role and sort
        const adminUsers = users.filter(user => user.is_superuser).sort((a, b) => a.email.localeCompare(b.email));
        const regularUsers = users.filter(user => !user.is_superuser).sort((a, b) => a.email.localeCompare(b.email));
        
        // Create option groups
        const createUserOption = (user, isCurrent = false) => {
            const displayName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
            const role = user.is_superuser ? 'ADMIN' : 'USER';
            const roleIcon = user.is_superuser ? '👑' : '👤';
            const currentLabel = isCurrent ? ' ✓ CURRENT' : '';
            const email = user.email || 'No email';
            
            return `
                <option value="${user.id}" 
                        data-email="${email}" 
                        data-username="${user.username}" 
                        data-role="${role.toLowerCase()}"
                        data-is-admin="${user.is_superuser}"
                        ${isCurrent ? 'selected' : ''}>
                    ${roleIcon} ${displayName} (${email}) - ${role}${currentLabel}
                </option>
            `;
        };

        const adminOptions = adminUsers.map(user => createUserOption(user, user.id === currentUserId)).join('');
        const regularOptions = regularUsers.map(user => createUserOption(user, user.id === currentUserId)).join('');

        return `
            <div class="user-switcher">
                <!-- Current User Display -->
                <div class="current-user-display">
                    <div class="current-user-info">
                        <div class="current-user-avatar">
                            <i class="material-icons">${currentUser?.is_superuser ? 'admin_panel_settings' : 'person'}</i>
                        </div>
                        <div class="current-user-details">
                            <div class="current-user-name">${currentUserDisplay}</div>
                            <div class="current-user-meta">
                                <span class="current-user-role ${currentUserRole.toLowerCase()}">${currentUserRole}</span>
                                <span class="current-user-id">ID: ${currentUserId}</span>
                            </div>
                            <div class="current-user-email">${currentUser?.email || 'No email'}</div>
                        </div>
                    </div>
                </div>

                <!-- Switch User Control -->
                <div class="user-switch-control">
                    <label for="user-select">
                        <i class="material-icons">swap_horiz</i> 
                        <span>Switch User</span>
                        <span class="dev-only-badge">DEV ONLY</span>
                    </label>
                    <select id="user-select" class="user-select">
                        <option value="">Choose user to switch to...</option>
                        ${adminOptions ? `<optgroup label="👑 ADMIN USERS (Full Access)">${adminOptions}</optgroup>` : ''}
                        ${regularOptions ? `<optgroup label="👤 REGULAR USERS (Limited Access)">${regularOptions}</optgroup>` : ''}
                    </select>
                    
                    <div class="switch-user-hint">
                        <i class="material-icons">info</i>
                        <span>Test accounts use default passwords</span>
                    </div>
                </div>
            </div>
        `;
    },

    createPasswordPromptModal(userEmail) {
        return `
            <div class="password-prompt-modal">
                <h3><i class="material-icons">key</i> Password Required</h3>
                <p>Please enter the password for <strong>${userEmail}</strong>:</p>
                <form id="password-prompt-form">
                    <div class="form-group">
                        <input type="password" id="switch-password" name="password" 
                               placeholder="Enter password" required autocomplete="new-password">
                        <small class="form-hint">
                            Try: <code>Password@123</code> for regular users or <code>Admin@123</code> for admin accounts
                        </small>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="ui.closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">
                            <i class="material-icons">login</i> Switch User
                        </button>
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
                    <button id="toggle-catalog" class="btn btn-outline catalog-toggle">
                        <i class="material-icons">menu_open</i> Show Endpoints
                    </button>
                    <button id="toggle-response" class="btn btn-outline response-toggle">
                        <i class="material-icons">receipt_long</i> Show Response
                    </button>
                </div>

                <!-- Catalog Overlay (for mobile) -->
                <div id="catalog-overlay" class="catalog-overlay"></div>

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

                    <!-- Middle Panel: Response Display -->
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

                    <!-- Right Panel: Endpoint Catalog -->
                    <div class="api-catalog-panel">
                        <div class="card">
                            <div class="card-header">
                                <h3><i class="material-icons">api</i> Available Endpoints</h3>
                                <button id="refresh-endpoints" class="btn btn-sm btn-outline">
                                    <i class="material-icons">refresh</i> Refresh
                                </button>
                            </div>
                            <div class="card-body">
                                <div id="endpoint-catalog" class="endpoint-catalog">
                                    <div class="catalog-loading">
                                        <i class="material-icons">hourglass_empty</i>
                                        <p>Loading endpoints...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    createUserDetailView(user) {
        return `
            <div class="user-detail-view">
                <div class="detail-section">
                    <h3>User Information</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>User ID:</label>
                            <span>${user.id}</span>
                        </div>
                        <div class="detail-item">
                            <label>Email:</label>
                            <span>${user.email}</span>
                        </div>
                        <div class="detail-item">
                            <label>Username:</label>
                            <span>${user.username || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Role:</label>
                            <span class="role-badge ${user.is_superuser ? 'admin' : 'user'}">
                                ${user.is_superuser ? 'Admin' : 'User'}
                            </span>
                        </div>
                        <div class="detail-item">
                            <label>Status:</label>
                            <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                                ${user.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <div class="detail-item">
                            <label>Created:</label>
                            <span>${new Date(user.created_at || Date.now()).toLocaleString()}</span>
                        </div>
                        <div class="detail-item">
                            <label>Last Login:</label>
                            <span>${user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Profile Complete:</label>
                            <span>${user.profile_completed ? 'Yes' : 'No'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Authentication</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>Google OAuth:</label>
                            <span>${user.google_id ? 'Linked' : 'Not linked'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Password Set:</label>
                            <span>${user.password_hash ? 'Yes' : 'No'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Email Verified:</label>
                            <span>${user.email_verified ? 'Yes' : 'No'}</span>
                        </div>
                    </div>
                </div>

                <div class="detail-actions">
                    <button class="btn btn-primary" onclick="app.loadUsers()">Back to Users</button>
                </div>
            </div>
        `;
    },

    createEnterpriseDetailView(enterprise) {
        return `
            <div class="enterprise-detail-view">
                <div class="detail-section">
                    <h3>Enterprise Information</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>Enterprise ID:</label>
                            <span>${enterprise.id}</span>
                        </div>
                        <div class="detail-item">
                            <label>Name:</label>
                            <span>${enterprise.name}</span>
                        </div>
                        <div class="detail-item">
                            <label>Email:</label>
                            <span>${enterprise.email || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Type:</label>
                            <span>${enterprise.type?.replace(/_/g, ' ') || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Tax Year:</label>
                            <span>${enterprise.tax_year || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Status:</label>
                            <span class="status-badge ${enterprise.is_active ? 'active' : 'inactive'}">
                                ${enterprise.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <div class="detail-item">
                            <label>Created:</label>
                            <span>${new Date(enterprise.created_at || Date.now()).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Ownership & Access</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>Owner ID:</label>
                            <span>${enterprise.owner_id || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Staff Members:</label>
                            <span>${enterprise.staff_ids?.length || 0}</span>
                        </div>
                        <div class="detail-item">
                            <label>Clients:</label>
                            <span>${enterprise.client_ids?.length || 0}</span>
                        </div>
                        <div class="detail-item">
                            <label>Total Users:</label>
                            <span>${(enterprise.staff_ids?.length || 0) + (enterprise.client_ids?.length || 0)}</span>
                        </div>
                    </div>
                </div>

                <div class="detail-actions">
                    <button class="btn btn-primary" onclick="app.loadEnterprises()">Back to Enterprises</button>
                </div>
            </div>
        `;
    },

    createAuthDebugPanel(authInfo) {
        return `
            <div class="auth-debug-panel">
                <div class="debug-section">
                    <h3>Token Information</h3>
                    <div class="debug-grid">
                        <div class="debug-item">
                            <label>Token Present:</label>
                            <span class="status-badge ${authInfo.token !== 'No token' ? 'active' : 'inactive'}">
                                ${authInfo.token !== 'No token' ? 'Yes' : 'No'}
                            </span>
                        </div>
                        <div class="debug-item">
                            <label>Token Preview:</label>
                            <span class="token-preview">${authInfo.token}</span>
                        </div>
                        <div class="debug-item">
                            <label>Token Length:</label>
                            <span>${authInfo.tokenLength} characters</span>
                        </div>
                    </div>
                </div>
                
                <div class="debug-section">
                    <h3>User Session</h3>
                    <div class="debug-grid">
                        <div class="debug-item">
                            <label>Authentication Status:</label>
                            <span class="status-badge ${authInfo.user ? 'active' : 'inactive'}">
                                ${authInfo.user ? 'Authenticated' : 'Not authenticated'}
                            </span>
                        </div>
                        ${authInfo.user ? `
                            <div class="debug-item">
                                <label>User ID:</label>
                                <span>${authInfo.user.id}</span>
                            </div>
                            <div class="debug-item">
                                <label>Email:</label>
                                <span>${authInfo.user.email}</span>
                            </div>
                            <div class="debug-item">
                                <label>Role:</label>
                                <span>${authInfo.user.is_superuser ? 'Admin' : 'User'}</span>
                            </div>
                        ` : ''}
                        ${authInfo.error ? `
                            <div class="debug-item error">
                                <label>Error:</label>
                                <span>${authInfo.error.detail || 'Unknown error'}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="debug-actions">
                    <button class="btn btn-sm btn-outline" onclick="app.refreshAuthInfo()">
                        <i class="material-icons">refresh</i> Refresh
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="api.clearToken(); app.refreshAuthInfo();">
                        <i class="material-icons">logout</i> Clear Token
                    </button>
                </div>
            </div>
        `;
    },

    createAuditDetailView(entry) {
        return `
            <div class="audit-detail-view">
                <div class="audit-detail-header">
                    <h3>Request Details</h3>
                    <div class="audit-meta">
                        <span class="audit-method ${entry.method.toLowerCase()}">${entry.method}</span>
                        <span class="audit-status status-${entry.status >= 200 && entry.status < 300 ? 'success' : 'error'}">
                            ${entry.status || 'ERR'}
                        </span>
                        <span class="audit-duration">${entry.duration}ms</span>
                    </div>
                </div>
                
                <div class="audit-detail-section">
                    <h4>Request</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>Timestamp:</label>
                            <span>${new Date(entry.timestamp).toLocaleString()}</span>
                        </div>
                        <div class="detail-item">
                            <label>Method:</label>
                            <span>${entry.method}</span>
                        </div>
                        <div class="detail-item">
                            <label>Path:</label>
                            <span>${entry.path}</span>
                        </div>
                    </div>
                    ${entry.data ? `
                        <div class="json-section">
                            <label>Request Data:</label>
                            <pre class="json-viewer">${JSON.stringify(entry.data, null, 2)}</pre>
                        </div>
                    ` : ''}
                </div>
                
                <div class="audit-detail-section">
                    <h4>Response</h4>
                    <div class="json-section">
                        <label>Response:</label>
                        <pre class="json-viewer">${JSON.stringify(entry.response, null, 2)}</pre>
                    </div>
                </div>
            </div>
        `;
    }
    // Add more components like tables, modals, etc. later
};
