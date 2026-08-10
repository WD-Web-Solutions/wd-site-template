from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated
from uuid import UUID

import stripe
from anthropic import AsyncAnthropic
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from site_api.core.config import Settings
from site_api.core.security import InvalidTokenError, decode_access_token
from site_api.core.storage import LocalFileStorage
from site_api.db.database import Database, DatabaseNotConfiguredError
from site_api.db.repositories import (
    SqlAlchemyAccountNoteRepository,
    SqlAlchemyAppointmentRepository,
    SqlAlchemyBlogPostRepository,
    SqlAlchemyCommentRepository,
    SqlAlchemyContactRequestRepository,
    SqlAlchemyMarketplaceItemRepository,
    SqlAlchemyOrderRepository,
    SqlAlchemyTagSubscriptionRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyWishlistRepository,
)
from site_api.domain.users import AuthenticatedUser, UserRole
from site_api.services.admin import AdminService
from site_api.services.auth import AuthService
from site_api.services.blog import BlogService
from site_api.services.chat import ChatService
from site_api.services.contact_requests import ContactRequestService
from site_api.services.marketplace import MarketplaceService
from site_api.services.scheduling import SchedulingService

_bearer_scheme = HTTPBearer(auto_error=False)


def _decode_bearer_token(
    credentials: HTTPAuthorizationCredentials, settings: Settings
) -> AuthenticatedUser:
    try:
        payload = decode_access_token(
            credentials.credentials,
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    except InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from error

    return AuthenticatedUser(
        id=UUID(payload["sub"]),
        email_address=payload["email"],
        full_name=payload["full_name"],
        role=UserRole(payload["role"]),
    )


def get_database(request: Request) -> Database:
    return request.app.state.database


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_session(
    database: Annotated[Database, Depends(get_database)],
) -> AsyncIterator[AsyncSession]:
    try:
        async with database.session() as session:
            yield session
    except DatabaseNotConfiguredError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured",
        ) from error


def get_contact_request_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ContactRequestService:
    repository = SqlAlchemyContactRequestRepository(session)
    return ContactRequestService(repository)


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_auth_service(
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(repository)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return _decode_bearer_token(credentials, settings)


async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedUser | None:
    if credentials is None:
        return None

    try:
        return _decode_bearer_token(credentials, settings)
    except HTTPException:
        return None


async def require_admin(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> AuthenticatedUser:
    if current_user.role is not UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_account_note_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyAccountNoteRepository:
    return SqlAlchemyAccountNoteRepository(session)


def get_admin_service(
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    note_repository: Annotated[
        SqlAlchemyAccountNoteRepository, Depends(get_account_note_repository)
    ],
) -> AdminService:
    return AdminService(user_repository, note_repository)


def get_blog_post_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyBlogPostRepository:
    return SqlAlchemyBlogPostRepository(session)


def get_comment_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyCommentRepository:
    return SqlAlchemyCommentRepository(session)


def get_tag_subscription_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyTagSubscriptionRepository:
    return SqlAlchemyTagSubscriptionRepository(session)


def get_blog_service(
    post_repository: Annotated[SqlAlchemyBlogPostRepository, Depends(get_blog_post_repository)],
    comment_repository: Annotated[SqlAlchemyCommentRepository, Depends(get_comment_repository)],
    subscription_repository: Annotated[
        SqlAlchemyTagSubscriptionRepository, Depends(get_tag_subscription_repository)
    ],
) -> BlogService:
    return BlogService(post_repository, comment_repository, subscription_repository)


def get_appointment_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyAppointmentRepository:
    return SqlAlchemyAppointmentRepository(session)


def get_scheduling_service(
    repository: Annotated[SqlAlchemyAppointmentRepository, Depends(get_appointment_repository)],
) -> SchedulingService:
    return SchedulingService(repository)


def get_file_storage(settings: Annotated[Settings, Depends(get_settings)]) -> LocalFileStorage:
    return LocalFileStorage(
        base_dir=Path(settings.blog_uploads_dir),
        base_url=f"{settings.api_prefix}/uploads/blog",
    )


def get_marketplace_file_storage(
    settings: Annotated[Settings, Depends(get_settings)],
) -> LocalFileStorage:
    return LocalFileStorage(
        base_dir=Path(settings.marketplace_uploads_dir),
        base_url=f"{settings.api_prefix}/uploads/marketplace",
    )


def get_anthropic_client(request: Request) -> AsyncAnthropic | None:
    return request.app.state.anthropic_client


def get_chat_service(
    client: Annotated[AsyncAnthropic | None, Depends(get_anthropic_client)],
    blog_repository: Annotated[SqlAlchemyBlogPostRepository, Depends(get_blog_post_repository)],
    appointment_repository: Annotated[
        SqlAlchemyAppointmentRepository, Depends(get_appointment_repository)
    ],
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatService:
    return ChatService(
        client, blog_repository, appointment_repository, user_repository, settings.chat_model
    )


def get_stripe_client(request: Request) -> stripe.StripeClient | None:
    return request.app.state.stripe_client


def get_marketplace_item_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyMarketplaceItemRepository:
    return SqlAlchemyMarketplaceItemRepository(session)


def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyOrderRepository:
    return SqlAlchemyOrderRepository(session)


def get_wishlist_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyWishlistRepository:
    return SqlAlchemyWishlistRepository(session)


def get_marketplace_service(
    item_repository: Annotated[
        SqlAlchemyMarketplaceItemRepository, Depends(get_marketplace_item_repository)
    ],
    order_repository: Annotated[SqlAlchemyOrderRepository, Depends(get_order_repository)],
    wishlist_repository: Annotated[
        SqlAlchemyWishlistRepository, Depends(get_wishlist_repository)
    ],
    stripe_client: Annotated[stripe.StripeClient | None, Depends(get_stripe_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> MarketplaceService:
    return MarketplaceService(
        item_repository,
        order_repository,
        wishlist_repository,
        stripe_client,
        settings.stripe_webhook_secret,
        settings.marketplace_currency,
        f"{settings.public_site_url}/marketplace/success?session_id={{CHECKOUT_SESSION_ID}}",
        f"{settings.public_site_url}/cart",
    )
