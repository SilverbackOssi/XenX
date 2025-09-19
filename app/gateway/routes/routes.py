
'''
ROUTE REGISTRY
'''
# TODO Import only router objects

from app.auth.routes import auth_routes, password_reset_routes, profile_routes
from app.auth.routes.google_oauth_router import router as google_oauth_router
from app.gateway.enterprises.routes import enterprise_routes, branding_routes, staff_routes
from app.gateway.users.admin.routes.admin_routes import admin_router

# Include microservices routers
# Tax Planner routes
from .service_routes.tax_planner import *
