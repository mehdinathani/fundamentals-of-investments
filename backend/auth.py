from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import secrets

security = HTTPBasic(auto_error=False)

# ─── Credentials ────────────────────────────────────────────────────
# Read from the environment (.env). Defaults preserve local dev.
AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASS = os.getenv("AUTH_PASS", "psx2026")

WWW_AUTH_HEADER = 'Basic realm="PSX Investment System"'


def verify(credentials: HTTPBasicCredentials | None):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": WWW_AUTH_HEADER},
        )
    is_valid = (
        secrets.compare_digest(credentials.username, AUTH_USER)
        and secrets.compare_digest(credentials.password, AUTH_PASS)
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": WWW_AUTH_HEADER},
        )
    return credentials.username


def require_auth(credentials: HTTPBasicCredentials | None = Depends(security)) -> str:
    """FastAPI dependency: validate Basic credentials, return the username."""
    return verify(credentials)
