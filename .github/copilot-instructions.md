# Copilot Instructions for XenX

## Project Overview
- **XenX** is a comprehensive API Gateway and User Management System built with FastAPI, serving as:
  - Central authentication & authorization provider
  - Single entry point for all client requests
  - User lifecycle and RBAC management system
  - Request router to microservices
  - Rate limiting & security enforcement layer

## Core Architecture
- **Tech Stack**: FastAPI, Python 3.11+, PostgreSQL, Redis, JWT
- **Major Components**:
  - `app/auth/`: Authentication, user management, RBAC
  - `app/core/`: Configuration, dependencies, system settings
  - `app/gateway/`: API routing, load balancing, service discovery
  - `app/middleware/`: Rate limiting, security, request validation

## User Roles & Access Patterns
- **Role Hierarchy**:
  - Administrator: Full platform access
  - CPA/Tax Professional: Client management, tax planning
  - Client: Limited to own data/documents
  - Staff: Organization-specific access
- **Access Control**: 
  - JWT-based authentication with refresh tokens
  - Organization-based data isolation
  - Rate limiting per user role
  - MFA support with TOTP

## Development Workflows

### Setup & Running
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run test suite
pytest

# Run specific test categories
pytest tests/auth/  # Auth tests only
pytest -m "not slow"  # Skip slow tests
```

### Database Management
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Key Integration Points
1. **Authentication Flow**:
   - Registration: `auth/routers/auth.py` -> `auth/services/auth_service.py`
   - Login: Returns JWT with user context, roles, permissions
   - MFA: Optional TOTP verification layer

2. **Service Communication**:
   - Gateway routes: `/api/{service}/{endpoint}`
   - Health checks: `/health` endpoint aggregates service status
   - Load balancing: Multiple service instance support

3. **Security Layers**:
   - Request validation & sanitization
   - Rate limiting via Redis
   - Token blacklisting for logout
   - MIME type validation for uploads

## Common Development Tasks

### Adding New Features
1. **New Endpoint**:
   ```python
   # auth/routers/auth.py
   @router.post("/login", response_model=schemas.TokenResponse)
   async def login(
       credentials: schemas.LoginRequest,
       auth_service: AuthService = Depends(get_auth_service)
   ):
       return await auth_service.authenticate(credentials)
   ```

2. **New Model**:
   - Add SQLAlchemy model in appropriate `models/` directory
   - Create Pydantic schema in `schemas/`
   - Generate migration with Alembic
   - Add service methods for CRUD operations

### Testing Patterns
- Test files mirror application structure
- Use `pytest` fixtures from `tests/conftest.py`
- Integration tests use `httpx.AsyncClient`
- Mock external services with `fakeredis`

## Performance Considerations
- Use Redis for caching and rate limiting
- Implement proper database indexing
- Consider async operations for I/O-bound tasks
- Monitor endpoint response times

## Error Handling
- Use standard HTTP status codes
- Return consistent error response format
- Log errors with proper context
- Handle service unavailability gracefully

---

Reference the comprehensive test specification in `TDD.md` for detailed implementation guidance.
