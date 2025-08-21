# Request-Based Tests for XenX API

This directory contains request-based tests for the Xentoba API. These tests make actual HTTP requests to a running instance of the API to verify functionality.

## Test Files

- `test_profile_update.py`: Tests for user profile management
- `test_enterprise_management.py`: Tests for enterprise management (creating, inviting users)
- `test_enterprise_branding.py`: Tests for enterprise branding features (logo, colors, footer text)
- `run_all_tests.py`: Main runner that executes all test files

## Prerequisites

1. The XenX server must be running at `http://localhost:8000`
2. Python packages:
   - requests
   - pillow (optional, for creating test images)

## Running Tests

### Running all tests
```
python run_all_tests.py
```

### Running specific test files
```
python test_profile_update.py
python test_enterprise_management.py
python test_enterprise_branding.py
```

## Test Data

The tests create test users and enterprises with the following pattern:
- Email: `<test_type>_<role>@example.com` (e.g., `branding_owner@example.com`)
- Username: `<test_type>_<role>` (e.g., `branding_owner`)
- Password: `Password@123`

## Notes

- Some tests may fail if dependent resources don't exist (e.g., logo upload without a test image)
- For invitation tests, we can't fully test the acceptance flow without direct access to the invitation token
- These tests are intentionally simple and don't clean up after themselves. In a production environment, consider adding cleanup steps.

## Adding New Tests

To add new test files:
1. Create a new Python file with the naming pattern `test_<feature_name>.py`
2. Define helper functions for API requests
3. Create a main function (e.g., `run_<feature>_tests()`) that executes the tests
4. Add the new test to `run_all_tests.py`
