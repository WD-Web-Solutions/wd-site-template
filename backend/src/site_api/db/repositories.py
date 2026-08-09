from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from site_api.db.models import (
    AccountNoteRecord,
    BlogPostRecord,
    CommentRecord,
    ContactRequestRecord,
    TagSubscriptionRecord,
    UserRecord,
)
from site_api.domain.account_notes import AccountNote
from site_api.domain.blog import (
    BlogPost,
    Comment,
    CommentNotFoundError,
    PostNotFoundError,
    PostStatus,
    TagSubscription,
)
from site_api.domain.contacts import ContactRequest
from site_api.domain.users import AccountStatus, User, UserNotFoundError, UserRole


def _to_domain_user(record: UserRecord) -> User:
    return User(
        id=record.id,
        email_address=record.email_address,
        full_name=record.full_name,
        hashed_password=record.hashed_password,
        role=UserRole(record.role),
        status=AccountStatus(record.status),
        created_at=record.created_at,
        last_login_at=record.last_login_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> User:
        self._session.add(
            UserRecord(
                id=user.id,
                email_address=user.email_address,
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                role=user.role.value,
                status=user.status.value,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
            )
        )
        await self._session.flush()
        return user

    async def get_by_email(self, email_address: str) -> User | None:
        result = await self._session.execute(
            select(UserRecord).where(UserRecord.email_address == email_address)
        )
        record = result.scalar_one_or_none()
        return None if record is None else _to_domain_user(record)

    async def get_by_id(self, user_id: UUID) -> User | None:
        record = await self._session.get(UserRecord, user_id)
        return None if record is None else _to_domain_user(record)

    async def list_all(self) -> list[User]:
        result = await self._session.execute(select(UserRecord).order_by(UserRecord.created_at))
        return [_to_domain_user(record) for record in result.scalars().all()]

    async def update_role(self, user_id: UUID, role: UserRole) -> User:
        record = await self._session.get(UserRecord, user_id)
        if record is None:
            raise UserNotFoundError
        record.role = role.value
        await self._session.flush()
        return _to_domain_user(record)

    async def update_status(self, user_id: UUID, status: AccountStatus) -> User:
        record = await self._session.get(UserRecord, user_id)
        if record is None:
            raise UserNotFoundError
        record.status = status.value
        await self._session.flush()
        return _to_domain_user(record)

    async def update_last_login(self, user_id: UUID, when: datetime) -> None:
        record = await self._session.get(UserRecord, user_id)
        if record is None:
            raise UserNotFoundError
        record.last_login_at = when
        await self._session.flush()


class SqlAlchemyAccountNoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, note: AccountNote) -> AccountNote:
        self._session.add(
            AccountNoteRecord(
                id=note.id,
                user_id=note.user_id,
                author_id=note.author_id,
                author_name=note.author_name,
                body=note.body,
                created_at=note.created_at,
            )
        )
        await self._session.flush()
        return note

    async def list_for_user(self, user_id: UUID) -> list[AccountNote]:
        result = await self._session.execute(
            select(AccountNoteRecord)
            .where(AccountNoteRecord.user_id == user_id)
            .order_by(AccountNoteRecord.created_at.desc())
        )
        return [
            AccountNote(
                id=record.id,
                user_id=record.user_id,
                author_id=record.author_id,
                author_name=record.author_name,
                body=record.body,
                created_at=record.created_at,
            )
            for record in result.scalars().all()
        ]


def _to_domain_post(record: BlogPostRecord) -> BlogPost:
    return BlogPost(
        id=record.id,
        title=record.title,
        slug=record.slug,
        excerpt=record.excerpt,
        body=record.body,
        cover_image_url=record.cover_image_url,
        tags=tuple(record.tags),
        author_id=record.author_id,
        author_name=record.author_name,
        status=PostStatus(record.status),
        published_at=record.published_at,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


class SqlAlchemyBlogPostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, post: BlogPost) -> BlogPost:
        self._session.add(
            BlogPostRecord(
                id=post.id,
                title=post.title,
                slug=post.slug,
                excerpt=post.excerpt,
                body=post.body,
                cover_image_url=post.cover_image_url,
                tags=list(post.tags),
                author_id=post.author_id,
                author_name=post.author_name,
                status=post.status.value,
                published_at=post.published_at,
                created_at=post.created_at,
                updated_at=post.updated_at,
            )
        )
        await self._session.flush()
        return post

    async def update(self, post: BlogPost) -> BlogPost:
        record = await self._session.get(BlogPostRecord, post.id)
        if record is None:
            raise PostNotFoundError
        record.title = post.title
        record.slug = post.slug
        record.excerpt = post.excerpt
        record.body = post.body
        record.cover_image_url = post.cover_image_url
        record.tags = list(post.tags)
        record.status = post.status.value
        record.published_at = post.published_at
        record.updated_at = post.updated_at
        await self._session.flush()
        return _to_domain_post(record)

    async def delete(self, post_id: UUID) -> None:
        record = await self._session.get(BlogPostRecord, post_id)
        if record is None:
            raise PostNotFoundError
        await self._session.delete(record)
        await self._session.flush()

    async def get_by_id(self, post_id: UUID) -> BlogPost | None:
        record = await self._session.get(BlogPostRecord, post_id)
        return None if record is None else _to_domain_post(record)

    async def get_by_slug(self, slug: str) -> BlogPost | None:
        result = await self._session.execute(
            select(BlogPostRecord).where(BlogPostRecord.slug == slug)
        )
        record = result.scalar_one_or_none()
        return None if record is None else _to_domain_post(record)

    async def slug_exists(self, slug: str) -> bool:
        result = await self._session.execute(
            select(BlogPostRecord.id).where(BlogPostRecord.slug == slug)
        )
        return result.scalar_one_or_none() is not None

    async def list_published(self, tag: str | None = None) -> list[BlogPost]:
        query = select(BlogPostRecord).where(BlogPostRecord.status == PostStatus.PUBLISHED.value)
        if tag is not None:
            query = query.where(BlogPostRecord.tags.any(tag))
        query = query.order_by(BlogPostRecord.published_at.desc())
        result = await self._session.execute(query)
        return [_to_domain_post(record) for record in result.scalars().all()]

    async def list_all(self) -> list[BlogPost]:
        result = await self._session.execute(
            select(BlogPostRecord).order_by(BlogPostRecord.created_at.desc())
        )
        return [_to_domain_post(record) for record in result.scalars().all()]

    async def list_distinct_published_tags(self) -> list[str]:
        result = await self._session.execute(
            select(BlogPostRecord.tags).where(BlogPostRecord.status == PostStatus.PUBLISHED.value)
        )
        tags: set[str] = set()
        for row in result.scalars().all():
            tags.update(row)
        return sorted(tags)


class SqlAlchemyCommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, comment: Comment) -> Comment:
        self._session.add(
            CommentRecord(
                id=comment.id,
                post_id=comment.post_id,
                author_id=comment.author_id,
                author_name=comment.author_name,
                body=comment.body,
                created_at=comment.created_at,
            )
        )
        await self._session.flush()
        return comment

    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        record = await self._session.get(CommentRecord, comment_id)
        return None if record is None else self._to_domain(record)

    async def list_for_post(self, post_id: UUID) -> list[Comment]:
        result = await self._session.execute(
            select(CommentRecord)
            .where(CommentRecord.post_id == post_id)
            .order_by(CommentRecord.created_at)
        )
        return [self._to_domain(record) for record in result.scalars().all()]

    async def delete(self, comment_id: UUID) -> None:
        record = await self._session.get(CommentRecord, comment_id)
        if record is None:
            raise CommentNotFoundError
        await self._session.delete(record)
        await self._session.flush()

    @staticmethod
    def _to_domain(record: CommentRecord) -> Comment:
        return Comment(
            id=record.id,
            post_id=record.post_id,
            author_id=record.author_id,
            author_name=record.author_name,
            body=record.body,
            created_at=record.created_at,
        )


class SqlAlchemyTagSubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, subscription: TagSubscription) -> TagSubscription:
        self._session.add(
            TagSubscriptionRecord(
                id=subscription.id,
                user_id=subscription.user_id,
                tag_name=subscription.tag_name,
                created_at=subscription.created_at,
            )
        )
        await self._session.flush()
        return subscription

    async def remove(self, user_id: UUID, tag_name: str) -> None:
        result = await self._session.execute(
            select(TagSubscriptionRecord).where(
                TagSubscriptionRecord.user_id == user_id,
                TagSubscriptionRecord.tag_name == tag_name,
            )
        )
        record = result.scalar_one_or_none()
        if record is not None:
            await self._session.delete(record)
            await self._session.flush()

    async def get(self, user_id: UUID, tag_name: str) -> TagSubscription | None:
        result = await self._session.execute(
            select(TagSubscriptionRecord).where(
                TagSubscriptionRecord.user_id == user_id,
                TagSubscriptionRecord.tag_name == tag_name,
            )
        )
        record = result.scalar_one_or_none()
        return None if record is None else self._to_domain(record)

    async def list_for_user(self, user_id: UUID) -> list[TagSubscription]:
        result = await self._session.execute(
            select(TagSubscriptionRecord)
            .where(TagSubscriptionRecord.user_id == user_id)
            .order_by(TagSubscriptionRecord.created_at)
        )
        return [self._to_domain(record) for record in result.scalars().all()]

    @staticmethod
    def _to_domain(record: TagSubscriptionRecord) -> TagSubscription:
        return TagSubscription(
            id=record.id,
            user_id=record.user_id,
            tag_name=record.tag_name,
            created_at=record.created_at,
        )


class SqlAlchemyContactRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, contact_request: ContactRequest) -> ContactRequest:
        self._session.add(
            ContactRequestRecord(
                id=contact_request.id,
                name=contact_request.name,
                email_address=contact_request.email_address,
                company=contact_request.company,
                phone=contact_request.phone,
                service=contact_request.service,
                message=contact_request.message,
                status=contact_request.status.value,
                created_at=contact_request.created_at,
            )
        )
        await self._session.flush()
        return contact_request
