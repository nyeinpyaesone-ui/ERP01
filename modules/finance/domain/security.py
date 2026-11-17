"""Validate Django SimpleJWT access tokens and require active staff users."""

import os

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)


async def require_staff(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication is required.")

    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise HTTPException(status_code=503, detail="Finance authentication is not configured.")

    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            options={"require": ["exp", "user_id", "token_type"]},
        )
        if claims.get("token_type") != "access":
            raise jwt.InvalidTokenError("Access token required.")
        user_id = int(claims["user_id"])
    except (jwt.PyJWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token.") from None

    user = await request.app.state.db.fetchrow(
        "SELECT id, is_active, is_staff, is_superuser FROM auth_user WHERE id = $1",
        user_id,
    )
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="User is inactive or does not exist.")
    if not (user["is_staff"] or user["is_superuser"]):
        raise HTTPException(status_code=403, detail="Staff permission is required.")

    return {"id": user["id"], "is_superuser": user["is_superuser"]}
