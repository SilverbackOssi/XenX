import enum

class StaffRole(str, enum.Enum):
    ADMIN = "admin"
    CPA = "cpa"
    ASSISTANT = "assistant"
    REVIEWER = "reviewer"

class StaffPermission(str, enum.Enum):
    """Defines the permission levels for a staff member within an enterprise."""

    FULL_ACCESS = "full_access"
    """Grants unrestricted access to all features, settings, and data within the enterprise.
    Typically reserved for the enterprise owner or top-level administrators.
    Can add/edit/remove staff, manage billing, and change enterprise-wide settings."""

    MANAGE = "manage"
    """Includes all 'EDIT' permissions, plus the ability to manage other staff members (invite,
    deactivate) and some enterprise-level settings."""

    EDIT = "edit"
    """Allows the user to create and modify data documents but not manage
    staff, clients, or change critical enterprise settings."""

    VIEW_ONLY = "view_only"
    """Restricts the user to only viewing data. They cannot create, edit, or delete any information."""
    
