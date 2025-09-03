
'''
ROUTE REGISTRY
'''
# TODO Import only router objects

from ..auth.routes import auth_routes, password_reset_routes
from ..auth.routes import profile_routes
from ..enterprises.routes import enterprise_routes, branding_routes, staff_routes
from .services.admin_routes import admin_router
from ..auth.routes.google_oauth_router import router as google_oauth_router

# Include microservices routers
# Tax Planner routes
from .services.tax_planner import project_router, strategy_router
