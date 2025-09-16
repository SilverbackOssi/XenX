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
        const tableRows = enterprises.map(enterprise => `
            <tr>
                <td>${enterprise.name}</td>
                <td>${enterprise.industry}</td>
                <td>${enterprise.owner_id}</td>
                <td class="actions">
                    <a data-id="${enterprise.id}" class="view-btn">View</a>
                    <a data-id="${enterprise.id}" class="edit-btn">Edit</a>
                    <a data-id="${enterprise.id}" class="delete-btn">Delete</a>
                </td>
            </tr>
        `).join('');

        return `
            <div class="card">
                <div class="card-header">
                    <h2>Enterprises</h2>
                    <button class="btn" id="add-enterprise-btn">Add Enterprise</button>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Industry</th>
                                <th>Owner ID</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    createEnterpriseForm(enterprise = {}) {
        return `
            <form id="enterprise-form">
                <input type="text" name="name" placeholder="Enterprise Name" value="${enterprise.name || ''}" required>
                <input type="text" name="industry" placeholder="Industry" value="${enterprise.industry || ''}" required>
                <textarea name="description" placeholder="Description">${enterprise.description || ''}</textarea>
                <button type="submit" class="btn">${enterprise.id ? 'Update' : 'Create'}</button>
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
    }
    // Add more components like tables, modals, etc. later
};
