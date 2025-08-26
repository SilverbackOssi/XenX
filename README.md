# XenX

Temporal interactive swagger docs: [here](https://xenx.onrender.com/docs)

Postman documentations: [here](https://documenter.getpostman.com/view/47600640/2sB3BHjoVH)

## Frontend Testing Interface

A robust frontend testing interface is now available to easily test all API endpoints. Access it by running the application and navigating to the root URL.

### Features:
- **Admin Panel**: Manage users, create superusers, and perform batch operations
- **Authentication**: Test login, registration, user profile management, and Google OAuth
- **Enterprises**: Manage enterprise data and branding
- **API Explorer**: Interactive tool to test any API endpoint with custom parameters

### Usage:
1. Start the application with `uvicorn main:app --reload`
2. Navigate to `http://localhost:8000/` in your browser
3. Use the navigation menu to access different testing sections

### Testing Google OAuth Sign-In
1. Go to the Auth page from the navigation menu
2. Click "Sign in with Google" button
3. Complete the Google authentication flow
4. You'll be redirected back to the application and automatically logged in

## Enterprise Branding API Endpoints

### Logo Management
- **POST** `/enterprises/{enterprise_id}/branding/logo` - Upload a logo for the enterprise
  - Accepts a file upload (multipart/form-data)
  - Stores the logo image and returns a URL reference
  - Replaces existing logo if one exists
  
- **DELETE** `/enterprises/{enterprise_id}/branding/logo` - Delete an enterprise's logo

### Branding Information
- **POST** `/enterprises/{enterprise_id}/branding` - Set branding information
  ```json
  {
    "primary_color": "#00FF00",
    "accent_color": "#0000FF",
    "footer_text": "© 2025 Zenco Tax. All rights reserved."
  }
  ```
  
- **PATCH** `/enterprises/{enterprise_id}/branding` - Update specific branding elements
  ```json
  {
    "primary_color": "#00FF00"
  }
  ```
  
- **GET** `/enterprises/{enterprise_id}/branding` - Retrieve all branding elements

All branding endpoints are protected and require authentication with appropriate permissions.