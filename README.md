# XenX

Temporal interactive swagger docs: [here](https://xenx.onrender.com/docs)

Postman documentations: [here](https://documenter.getpostman.com/view/47600640/2sB3BHjoVH)

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