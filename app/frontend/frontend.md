# XenX Frontend Testing Interface

## Purpose

This frontend app is a developer-focused testing interface for the XenX backend. It is designed to allow developers to interact with, validate, and debug backend features before the production frontend is integrated.

## Key Features

- **Comprehensive Testing UI:** Provides forms, navigation, and interactive elements to test authentication, enterprise management, admin panel, and microservices.
- **API Explorer:** Enables direct testing of backend endpoints, including health checks, login, registration, and more.
- **Manual Validation:** Supports manual testing of critical user scenarios, such as login flows, enterprise branding, and database initialization.
- **Static Assets:** Includes basic CSS and JS for UI components, routing, and API calls, focused on functionality over design.

## Usage

Developers use this interface to:

- Validate backend endpoints and flows
- Simulate user actions (login, registration, enterprise management)
- Debug backend responses and error handling
- Ensure database and API initialization

## Integration Notes

This app is **not** intended for end users. It is a temporary tool for backend development and testing. Once the live frontend is ready, this interface will be replaced or removed.

---

**Location:** `/app/frontend/`
**Entry Point:** `index.html`
**Static Assets:** `/static/css/style.css`, `/static/js/`
