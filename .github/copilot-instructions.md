# XenToba Gateway & User Management System

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

- Bootstrap and run the repository:
  - `pip install -r requirements.txt` -- takes 30 seconds to complete. NEVER CANCEL.
  - `uvicorn main:app --reload --port 8000 --host 0.0.0.0` -- starts in 1-2 seconds, auto-initializes databases. NEVER CANCEL.
  - Access web interface at http://localhost:8000/ and API docs at http://localhost:8000/api/v1/docs

- Run tests:
  - Unit tests: `PYTHONPATH=. pytest tests/auth/unit/test_user_registration.py -v` -- takes 8 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
  - **WARNING**: Most tests currently fail with 404 errors due to endpoint mismatches. Tests expect different API structure than current implementation.
  - Request-based tests: `python tests/request_based/run_all_tests.py` -- also fail due to endpoint mismatches.

- Lint and format code:
  - `flake8 --max-line-length=88 --exclude=venv,__pycache__,.git,uploads app/` -- takes <1 second, shows ~1000 style issues.
  - `black --check app/` -- takes 1 second, shows many files need reformatting.
  - `isort --check-only app/` -- checks import sorting.
  - Always run linting before committing changes.

## Validation

- **MANUAL VALIDATION REQUIREMENT**: After making any changes, ALWAYS test functionality through the web interface.
- **CRITICAL USER SCENARIOS TO TEST**:
  1. **Authentication Flow**: Navigate to http://localhost:8000/auth, test login/registration forms, Google OAuth button
  2. **Admin Panel**: Navigate to /admin, test user management features
  3. **Enterprise Management**: Navigate to /enterprises, test enterprise and branding features
  4. **API Explorer**: Navigate to /api-explorer, test common endpoints like GET /health, POST /auth/login
  5. **Database Verification**: Confirm databases auto-initialize on startup (watch startup logs)

- **Database Behavior**: SQLite databases (users.db, tax_planner.db) reset between runs. Tables auto-create on startup.
- **API Structure**: All API endpoints are under `/api/v1/` prefix. Health check: `/api/v1/health`

## Common Tasks

### Repository Structure
```
/home/runner/work/XenX/XenX/
├── main.py                 # FastAPI application entry point  
├── requirements.txt        # Python dependencies
├── pytest.ini            # Test configuration
├── .env.example           # Environment configuration template
├── app/                   # Main application code
│   ├── auth/              # Authentication system
│   ├── enterprises/       # Enterprise management  
│   ├── microservices/     # Tax planner microservices
│   └── frontend/          # Web testing interface
├── tests/                 # Test suites (currently have endpoint mismatches)
│   ├── auth/unit/         # Unit tests (use PYTHONPATH=. to run)
│   └── request_based/     # Integration tests
├── users.db               # SQLite user database (auto-created)
└── tax_planner.db         # SQLite tax planner database (auto-created)
```

### Key Dependencies (from requirements.txt)
- FastAPI 0.116.1 + uvicorn for web framework
- SQLAlchemy 2.0.43 for database ORM
- pytest + pytest-cov for testing
- black + flake8 + isort for code quality
- Google auth libraries for OAuth
- bcrypt for password hashing

### Application Features
- **Web Interface**: Full-featured testing interface with navigation menu
- **Authentication**: Login/register forms + Google OAuth integration
- **Enterprise Management**: Branding, staff, client management
- **Tax Planning**: Project and strategy management microservice
- **Admin Panel**: User management and administrative functions
- **API Explorer**: Interactive endpoint testing with pre-populated examples

### Environment Setup
- Python 3.12.3 required
- No external databases needed (uses SQLite with auto-initialization)
- Optional: Configure Google OAuth via .env file (copy from .env.example)
- **Database Note**: DB is NOT persistent - data resets between application restarts

### Timing Expectations
- **Dependency Installation**: 30 seconds - NEVER CANCEL, set timeout to 60+ seconds
- **Application Startup**: 1-2 seconds including database initialization - NEVER CANCEL  
- **Unit Tests**: 8 seconds per test file - NEVER CANCEL, set timeout to 30+ seconds
- **Linting**: <1 second for full codebase scan
- **Formatting**: 1 second for full codebase check

### Current Test Status
- **Unit Tests**: Run but fail due to API endpoint mismatches (expect 5 failures in test_user_registration.py)
- **Integration Tests**: Also fail due to endpoint structure changes
- **Coverage**: Shows 44% when tests execute despite failures
- **Recommendation**: Focus on manual validation through web interface rather than automated tests until endpoints are aligned

### Known Issues
- Tests were written for different API structure than current implementation
- ~1000 flake8 style issues exist in codebase
- Many files need black formatting
- Some tests have import errors (e.g., UserRole import missing)
- External CDN resources blocked in testing environment (cosmetic only)

### Code Quality Commands
Always run before committing:
```bash
flake8 --max-line-length=88 --exclude=venv,__pycache__,.git,uploads app/
black --check app/
isort --check-only app/
```

### Manual Testing Checklist
After any code changes, verify:
- [ ] Application starts without errors
- [ ] Web interface loads at http://localhost:8000/
- [ ] API health endpoint responds: `curl http://localhost:8000/api/v1/health`
- [ ] Navigation menu works (Home, Auth, Admin, Enterprises, API Explorer)
- [ ] Forms render correctly on /auth page
- [ ] API Explorer shows common endpoints
- [ ] Database initialization completes (check startup logs)

**Remember**: This is a development/testing application with a comprehensive web interface. The web interface IS the primary testing tool - use it extensively to validate any changes you make.