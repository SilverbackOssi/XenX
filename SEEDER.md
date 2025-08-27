# Seeder Documentation

This document provides information about the database seeder included in the XenX application.

## Overview

The database seeder populates the database with test data for development and testing purposes. The seeder creates:

- 1 admin user
- 9 regular users
- 6 enterprises (4 users with 1 enterprise each, 2 users with 2 enterprises each)
- 5 additional users (2 clients, 3 staff members)
- Client and staff associations

## Admin User Credentials

```
Email: testadmin@xentoba.com
Password: Admin@123
```

## Regular Users

All regular users have the password: `Password@123`

## Running the Seeder

### Automatic Startup

The seeder automatically runs during application startup if either:
- The `ENVIRONMENT` is set to `development`, or
- The `RUN_SEEDER_ON_STARTUP` environment variable is set to `true`

### Manual Execution

You can also run the seeder manually using the provided script:

```bash
python run_seeder.py
```

## Configuration

The seeder behavior can be controlled through environment variables:

- `RUN_SEEDER_ON_STARTUP`: When set to `true`, runs the seeder on application startup (default: `false`)
- `CLEAR_DB_BEFORE_SEED`: When set to `true`, clears existing data before seeding (default: `true`)
- `ENVIRONMENT`: When set to `development`, enables seeder on startup (default: `development`)

You can set these variables in your `.env` file.

## Generated Data

The seeder generates realistic-looking test data using the Faker library, including:
- User profiles with names, emails, and phone numbers
- Enterprise information with company names, addresses, etc.
- Staff members with different roles
- Client accounts linked to enterprises
