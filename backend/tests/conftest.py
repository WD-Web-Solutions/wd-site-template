from collections.abc import Iterator
from dataclasses import replace
from datetime import datetime
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from site_api.core.config import Settings
from site_api.domain.account_notes import AccountNote
from site_api.domain.blog import (
    BlogPost,
    Comment,
    CommentNotFoundError,
    PostNotFoundError,
    TagSubscription,
)
from site_api.domain.contacts import ContactRequest
from site_api.domain.scheduling import Appointment, AppointmentStatus, SlotNotFoundError
from site_api.domain.users import AccountStatus, User, UserNotFoundError, UserRole
from site_api.main import create_app
from site_api.services.admin import AdminService
from site_api.services.auth import AuthService
from site_api.services.blog import BlogService
from site_api.services.chat import ChatService
from site_api.services.contact_requests import ContactRequestService
from site_api.services.scheduling import SchedulingService


class InMemoryContactRequestRepository:
    def __init__(self) -> None:
        self.contact_requests: list[ContactRequest] = []

    async def add(self, contact_request: ContactRequest) -> ContactRequest:
        self.contact_requests.append(contact_request)
        return contact_request


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: list[User] = []

    async def add(self, user: User) -> User:
        self.users.append(user)
        return user

    async def get_by_email(self, email_address: str) -> User | None:
        for user in self.users:
            if user.email_address == email_address:
                return user
        return None

    async def get_by_id(self, user_id: UUID) -> User | None:
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    async def list_all(self) -> list[User]:
        return list(self.users)

    async def update_role(self, user_id: UUID, role: UserRole) -> User:
        return self._replace(user_id, role=role)

    async def update_status(self, user_id: UUID, status: AccountStatus) -> User:
        return self._replace(user_id, status=status)

    async def update_last_login(self, user_id: UUID, when: datetime) -> None:
        self._replace(user_id, last_login_at=when)

    def _replace(self, user_id: UUID, **changes: object) -> User:
        for index, user in enumerate(self.users):
            if user.id == user_id:
                updated = replace(user, **changes)
                self.users[index] = updated
                return updated
        raise UserNotFoundError


class InMemoryAccountNoteRepository:
    def __init__(self) -> None:
        self.notes: list[AccountNote] = []

    async def add(self, note: AccountNote) -> AccountNote:
        self.notes.append(note)
        return note

    async def list_for_user(self, user_id: UUID) -> list[AccountNote]:
        return [note for note in self.notes if note.user_id == user_id]


class InMemoryBlogPostRepository:
    def __init__(self) -> None:
        self.posts: list[BlogPost] = []

    async def add(self, post: BlogPost) -> BlogPost:
        self.posts.append(post)
        return post

    async def update(self, post: BlogPost) -> BlogPost:
        for index, existing in enumerate(self.posts):
            if existing.id == post.id:
                self.posts[index] = post
                return post
        raise PostNotFoundError

    async def delete(self, post_id: UUID) -> None:
        for index, post in enumerate(self.posts):
            if post.id == post_id:
                del self.posts[index]
                return
        raise PostNotFoundError

    async def get_by_id(self, post_id: UUID) -> BlogPost | None:
        for post in self.posts:
            if post.id == post_id:
                return post
        return None

    async def get_by_slug(self, slug: str) -> BlogPost | None:
        for post in self.posts:
            if post.slug == slug:
                return post
        return None

    async def slug_exists(self, slug: str) -> bool:
        return any(post.slug == slug for post in self.posts)

    async def list_published(self, tag: str | None = None) -> list[BlogPost]:
        from site_api.domain.blog import PostStatus

        results = [post for post in self.posts if post.status is PostStatus.PUBLISHED]
        if tag is not None:
            results = [post for post in results if tag in post.tags]
        return sorted(results, key=lambda post: post.published_at or post.created_at, reverse=True)

    async def list_all(self) -> list[BlogPost]:
        return sorted(self.posts, key=lambda post: post.created_at, reverse=True)

    async def list_distinct_published_tags(self) -> list[str]:
        from site_api.domain.blog import PostStatus

        tags: set[str] = set()
        for post in self.posts:
            if post.status is PostStatus.PUBLISHED:
                tags.update(post.tags)
        return sorted(tags)


class InMemoryCommentRepository:
    def __init__(self) -> None:
        self.comments: list[Comment] = []

    async def add(self, comment: Comment) -> Comment:
        self.comments.append(comment)
        return comment

    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        for comment in self.comments:
            if comment.id == comment_id:
                return comment
        return None

    async def list_for_post(self, post_id: UUID) -> list[Comment]:
        return [comment for comment in self.comments if comment.post_id == post_id]

    async def delete(self, comment_id: UUID) -> None:
        for index, comment in enumerate(self.comments):
            if comment.id == comment_id:
                del self.comments[index]
                return
        raise CommentNotFoundError


class InMemoryTagSubscriptionRepository:
    def __init__(self) -> None:
        self.subscriptions: list[TagSubscription] = []

    async def add(self, subscription: TagSubscription) -> TagSubscription:
        self.subscriptions.append(subscription)
        return subscription

    async def remove(self, user_id: UUID, tag_name: str) -> None:
        self.subscriptions = [
            sub
            for sub in self.subscriptions
            if not (sub.user_id == user_id and sub.tag_name == tag_name)
        ]

    async def get(self, user_id: UUID, tag_name: str) -> TagSubscription | None:
        for sub in self.subscriptions:
            if sub.user_id == user_id and sub.tag_name == tag_name:
                return sub
        return None

    async def list_for_user(self, user_id: UUID) -> list[TagSubscription]:
        return [sub for sub in self.subscriptions if sub.user_id == user_id]


class InMemoryAppointmentRepository:
    def __init__(self) -> None:
        self.appointments: list[Appointment] = []

    async def add(self, appointment: Appointment) -> Appointment:
        self.appointments.append(appointment)
        return appointment

    async def update(self, appointment: Appointment) -> Appointment:
        for index, existing in enumerate(self.appointments):
            if existing.id == appointment.id:
                self.appointments[index] = appointment
                return appointment
        raise SlotNotFoundError

    async def delete(self, appointment_id: UUID) -> None:
        for index, appointment in enumerate(self.appointments):
            if appointment.id == appointment_id:
                del self.appointments[index]
                return
        raise SlotNotFoundError

    async def get_by_id(self, appointment_id: UUID) -> Appointment | None:
        for appointment in self.appointments:
            if appointment.id == appointment_id:
                return appointment
        return None

    async def list_open_upcoming(self, now: datetime) -> list[Appointment]:
        results = [
            appointment
            for appointment in self.appointments
            if appointment.status is AppointmentStatus.OPEN and appointment.starts_at >= now
        ]
        return sorted(results, key=lambda appointment: appointment.starts_at)

    async def list_for_client(self, client_id: UUID) -> list[Appointment]:
        results = [
            appointment for appointment in self.appointments if appointment.client_id == client_id
        ]
        return sorted(results, key=lambda appointment: appointment.starts_at, reverse=True)

    async def list_all(self, status: AppointmentStatus | None = None) -> list[Appointment]:
        results = self.appointments
        if status is not None:
            results = [appointment for appointment in results if appointment.status is status]
        return sorted(results, key=lambda appointment: appointment.starts_at, reverse=True)


class FakeAnthropicTextBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class FakeAnthropicMessage:
    def __init__(self, text: str) -> None:
        self.content = [FakeAnthropicTextBlock(text)]


class FakeAnthropicMessages:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.last_kwargs: dict[str, object] | None = None

    async def create(self, **kwargs: object) -> FakeAnthropicMessage:
        self.last_kwargs = kwargs
        return FakeAnthropicMessage(self.reply)


class FakeAnthropicClient:
    def __init__(self, reply: str = "Hello! How can I help?") -> None:
        self.messages = FakeAnthropicMessages(reply)


class FakeFileStorage:
    def __init__(self) -> None:
        self.saved: list[tuple[bytes, str]] = []

    async def save_image(self, content: bytes, content_type: str) -> str:
        from site_api.domain.storage import (
            FileTooLargeError,
            UnsupportedFileTypeError,
        )

        if content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
            raise UnsupportedFileTypeError
        if len(content) > 5 * 1024 * 1024:
            raise FileTooLargeError

        self.saved.append((content, content_type))
        return f"/api/uploads/blog/fake-{len(self.saved)}.jpg"


@pytest.fixture
def repository() -> InMemoryContactRequestRepository:
    return InMemoryContactRequestRepository()


@pytest.fixture
def contact_service(
    repository: InMemoryContactRequestRepository,
) -> ContactRequestService:
    return ContactRequestService(repository)


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def note_repository() -> InMemoryAccountNoteRepository:
    return InMemoryAccountNoteRepository()


@pytest.fixture
def auth_service(user_repository: InMemoryUserRepository) -> AuthService:
    return AuthService(user_repository)


@pytest.fixture
def admin_service(
    user_repository: InMemoryUserRepository,
    note_repository: InMemoryAccountNoteRepository,
) -> AdminService:
    return AdminService(user_repository, note_repository)


@pytest.fixture
def blog_post_repository() -> InMemoryBlogPostRepository:
    return InMemoryBlogPostRepository()


@pytest.fixture
def comment_repository() -> InMemoryCommentRepository:
    return InMemoryCommentRepository()


@pytest.fixture
def tag_subscription_repository() -> InMemoryTagSubscriptionRepository:
    return InMemoryTagSubscriptionRepository()


@pytest.fixture
def file_storage() -> FakeFileStorage:
    return FakeFileStorage()


@pytest.fixture
def appointment_repository() -> InMemoryAppointmentRepository:
    return InMemoryAppointmentRepository()


@pytest.fixture
def scheduling_service(
    appointment_repository: InMemoryAppointmentRepository,
) -> SchedulingService:
    return SchedulingService(appointment_repository)


@pytest.fixture
def blog_service(
    blog_post_repository: InMemoryBlogPostRepository,
    comment_repository: InMemoryCommentRepository,
    tag_subscription_repository: InMemoryTagSubscriptionRepository,
) -> BlogService:
    return BlogService(blog_post_repository, comment_repository, tag_subscription_repository)


@pytest.fixture
def fake_anthropic_client() -> FakeAnthropicClient:
    return FakeAnthropicClient()


@pytest.fixture
def chat_service(
    fake_anthropic_client: FakeAnthropicClient,
    blog_post_repository: InMemoryBlogPostRepository,
    appointment_repository: InMemoryAppointmentRepository,
    user_repository: InMemoryUserRepository,
) -> ChatService:
    return ChatService(
        fake_anthropic_client,  # type: ignore[arg-type]
        blog_post_repository,
        appointment_repository,
        user_repository,
        "claude-opus-5",
    )


@pytest.fixture
def app(
    contact_service: ContactRequestService,
    auth_service: AuthService,
    admin_service: AdminService,
    blog_service: BlogService,
    file_storage: FakeFileStorage,
    scheduling_service: SchedulingService,
    chat_service: ChatService,
) -> FastAPI:
    settings = Settings(environment="test", cors_origins=[], database_url=None)
    return create_app(
        settings,
        contact_service_provider=lambda: contact_service,
        auth_service_provider=lambda: auth_service,
        admin_service_provider=lambda: admin_service,
        blog_service_provider=lambda: blog_service,
        file_storage_provider=lambda: file_storage,
        scheduling_service_provider=lambda: scheduling_service,
        chat_service_provider=lambda: chat_service,
    )


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
