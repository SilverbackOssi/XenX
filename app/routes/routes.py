
'''
ROUTE REGISTRY
'''

from ..auth.routes import auth_routes, password_reset_routes
from ..auth.routes import profile_routes
from ..enterprises.routes import enterprise_routes, branding_routes, staff_routes
from . import admin_routes


from app.auth.routes.google_oauth_router import router as google_oauth_router
