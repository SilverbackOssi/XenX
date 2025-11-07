# XenToba Gateway & User Management System

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


### Known Issues
- Tests were written for different API structure than current implementation
- ~1000 flake8 style issues exist in codebase
- Many files need black formatting
- Some tests have import errors (e.g., UserRole import missing)
- External CDN resources blocked in testing environment (cosmetic only)
- Google OAuth requires valid credentials in .env file (not provided)

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