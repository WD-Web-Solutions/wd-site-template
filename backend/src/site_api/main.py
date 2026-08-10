from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from anthropic import AsyncAnthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from site_api.api.dependencies import (
    get_admin_service,
    get_auth_service,
    get_blog_service,
    get_chat_service,
    get_contact_request_service,
    get_file_storage,
    get_scheduling_service,
)
from site_api.api.routes import (
    admin,
    auth,
    blog,
    blog_admin,
    chat,
    contact_requests,
    health,
    scheduling,
    scheduling_admin,
)
from site_api.core.config import Settings
from site_api.core.logging import configure_logging
from site_api.db.database import Database
from site_api.domain.storage import FileStorage
from site_api.services.admin import AdminService
from site_api.services.auth import AuthService
from site_api.services.blog import BlogService
from site_api.services.chat import ChatService
from site_api.services.contact_requests import ContactRequestService
from site_api.services.scheduling import SchedulingService

ContactServiceProvider = Callable[[], ContactRequestService]
AuthServiceProvider = Callable[[], AuthService]
AdminServiceProvider = Callable[[], AdminService]
BlogServiceProvider = Callable[[], BlogService]
FileStorageProvider = Callable[[], FileStorage]
SchedulingServiceProvider = Callable[[], SchedulingService]
ChatServiceProvider = Callable[[], ChatService]


def create_app(
    settings: Settings | None = None,
    contact_service_provider: ContactServiceProvider | None = None,
    auth_service_provider: AuthServiceProvider | None = None,
    admin_service_provider: AdminServiceProvider | None = None,
    blog_service_provider: BlogServiceProvider | None = None,
    file_storage_provider: FileStorageProvider | None = None,
    scheduling_service_provider: SchedulingServiceProvider | None = None,
    chat_service_provider: ChatServiceProvider | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings()
    configure_logging(resolved_settings.log_level)
    database = Database(resolved_settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await database.dispose()

    application = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    application.state.database = database
    application.state.settings = resolved_settings
    application.state.anthropic_client = (
        AsyncAnthropic(api_key=resolved_settings.anthropic_api_key)
        if resolved_settings.anthropic_api_key
        else None
    )

    if resolved_settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=resolved_settings.cors_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )

    application.mount(
        f"{resolved_settings.api_prefix}/uploads/blog",
        StaticFiles(directory=str(Path(resolved_settings.blog_uploads_dir)), check_dir=False),
        name="blog-uploads",
    )

    application.include_router(health.router, prefix=resolved_settings.api_prefix)
    application.include_router(contact_requests.router, prefix=resolved_settings.api_prefix)
    application.include_router(auth.router, prefix=resolved_settings.api_prefix)
    application.include_router(admin.router, prefix=resolved_settings.api_prefix)
    application.include_router(blog.router, prefix=resolved_settings.api_prefix)
    application.include_router(blog_admin.router, prefix=resolved_settings.api_prefix)
    application.include_router(scheduling.router, prefix=resolved_settings.api_prefix)
    application.include_router(scheduling_admin.router, prefix=resolved_settings.api_prefix)
    application.include_router(chat.router, prefix=resolved_settings.api_prefix)

    if contact_service_provider is not None:
        application.dependency_overrides[get_contact_request_service] = contact_service_provider

    if auth_service_provider is not None:
        application.dependency_overrides[get_auth_service] = auth_service_provider

    if admin_service_provider is not None:
        application.dependency_overrides[get_admin_service] = admin_service_provider

    if blog_service_provider is not None:
        application.dependency_overrides[get_blog_service] = blog_service_provider

    if file_storage_provider is not None:
        application.dependency_overrides[get_file_storage] = file_storage_provider

    if scheduling_service_provider is not None:
        application.dependency_overrides[get_scheduling_service] = scheduling_service_provider

    if chat_service_provider is not None:
        application.dependency_overrides[get_chat_service] = chat_service_provider

    return application


app = create_app()
