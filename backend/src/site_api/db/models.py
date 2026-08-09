from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    email_address: Mapped[str] = mapped_column(String(254), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AccountNoteRecord(Base):
    __tablename__ = "account_notes"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    author_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("users.id"))
    author_name: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class BlogPostRecord(Base):
    __tablename__ = "blog_posts"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220), unique=True)
    excerpt: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(60)))
    author_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("users.id"))
    author_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class CommentRecord(Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    post_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("blog_posts.id"), index=True
    )
    author_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("users.id"))
    author_name: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class TagSubscriptionRecord(Base):
    __tablename__ = "tag_subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", "tag_name", name="uq_tag_subscriptions_user_tag"),
    )

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    tag_name: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class ContactRequestRecord(Base):
    __tablename__ = "contact_requests"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email_address: Mapped[str] = mapped_column(String(254))
    company: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(40))
    service: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="received")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
