from __future__ import annotations

import logging
import os
import uuid
from typing import AsyncGenerator, Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from backend.app.services.db.engine import get_engine, get_session_factory
from .config import get_settings

logger = logging.getLogger("neura.auth")

# Auth-specific engine/session (only used when NEURA_AUTH_DB_URL override is set)
_auth_engine = None
_auth_session_factory = None


Base = declarative_base()


def _has_auth_db_override() -> bool:
    """Check if a separate auth database URL is configured."""
    return bool(os.getenv("NEURA_AUTH_DB_URL"))


def _get_auth_engine():
    """Get the auth-specific engine when NEURA_AUTH_DB_URL is set."""
    global _auth_engine, _auth_session_factory
    if _auth_engine is None:
        url = os.getenv("NEURA_AUTH_DB_URL")
        connect_args = {}
        if url and "sqlite" in url:
            connect_args = {"check_same_thread": False}
        _auth_engine = create_async_engine(url, connect_args=connect_args)
        _auth_session_factory = async_sessionmaker(_auth_engine, expire_on_commit=False)
        logger.info(
            "auth_db_override_active",
            extra={"event": "auth_db_override_active", "dialect": url.split(":")[0] if ":" in url else "unknown"},
        )
    return _auth_engine


def _get_auth_session_factory():
    """Get the session factory for auth -- uses override or centralized engine."""
    if _has_auth_db_override():
        if _auth_session_factory is None:
            _get_auth_engine()
        return _auth_session_factory
    # Default: use the centralized engine from backend.app.db.engine
    return get_session_factory()


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "auth_users"
    full_name = Column(String, nullable=True)


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    session_factory = _get_auth_session_factory()
    async with session_factory() as session:
        yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret: str = ""
    verification_token_secret: str = ""

    def __init__(self, user_db: SQLAlchemyUserDatabase):
        super().__init__(user_db)
        settings = get_settings()
        self.reset_password_token_secret = settings.jwt_secret.get_secret_value()
        self.verification_token_secret = settings.jwt_secret.get_secret_value()

    async def on_after_register(self, user: User, request: Optional[Request] = None) -> None:
        return None


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    settings = get_settings()
    return JWTStrategy(
        secret=settings.jwt_secret.get_secret_value(),
        lifetime_seconds=settings.jwt_lifetime_seconds,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)
current_optional_user = fastapi_users.current_user(optional=True)


async def init_auth_db() -> None:
    """Create auth tables. Uses override engine if NEURA_AUTH_DB_URL is set."""
    if _has_auth_db_override():
        engine = _get_auth_engine()
    else:
        engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("auth_db_initialized", extra={"event": "auth_db_initialized"})
