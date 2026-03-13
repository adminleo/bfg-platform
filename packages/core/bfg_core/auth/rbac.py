"""Role-Based Access Control (RBAC) — simple role checker for routes.

Usage in routes (check in the handler itself):
    from bfg_core.auth.rbac import require_role

    @router.get("/coach/dashboard")
    async def dashboard(user: User = Depends(get_current_user)):
        require_role(user, "coach", "admin")
        ...
"""

from fastapi import HTTPException, status
from bfg_core.models.user import User


def require_role(user: User, *allowed_roles: str) -> None:
    """Check that user.role is in allowed_roles.

    Raises HTTP 403 Forbidden if not authorized.

    Args:
        user: The authenticated user object.
        *allowed_roles: One or more role strings, e.g. "coach", "admin".
    """
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Zugriff verweigert. Erforderliche Rolle: {', '.join(sorted(allowed_roles))}",
        )
