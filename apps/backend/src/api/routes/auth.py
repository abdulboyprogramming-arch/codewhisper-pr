# ============================================================
# CodeWhisper PR - Authentication Routes
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
)
from src.services.auth_service import AuthService
from src.core.exceptions import AuthenticationError

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name,
        )
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(
            email=request.email,
            password=request.password,
        )
        tokens = await auth_service.create_tokens(user)

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
            user=UserResponse.model_validate(user),
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.refresh_tokens(request.refresh_token)
        user = await auth_service.get_user_from_token(request.refresh_token)

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
            user=UserResponse.model_validate(user),
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        await auth_service.revoke_token(token)
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        user = await auth_service.verify_token(token)
        return UserResponse.model_validate(user)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Get user info failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user info")
