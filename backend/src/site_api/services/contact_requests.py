from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from loguru import logger

from site_api.domain.contacts import (
    ContactRequest,
    ContactRequestNotFoundError,
    ContactRequestRepository,
    ContactRequestStatus,
)


@dataclass(frozen=True, slots=True)
class SubmitContactRequest:
    name: str
    email_address: str
    company: str | None
    phone: str | None
    service: str
    message: str


class ContactRequestService:
    def __init__(
        self,
        repository: ContactRequestRepository,
        id_factory: Callable[[], UUID] = uuid4,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._repository = repository
        self._id_factory = id_factory
        self._clock = clock

    async def submit(self, command: SubmitContactRequest) -> ContactRequest:
        now = self._clock()
        contact_request = ContactRequest(
            id=self._id_factory(),
            name=command.name,
            email_address=command.email_address,
            company=command.company,
            phone=command.phone,
            service=command.service,
            message=command.message,
            status=ContactRequestStatus.RECEIVED,
            created_at=now,
            updated_at=now,
        )
        saved_request = await self._repository.add(contact_request)
        logger.bind(contact_request_id=str(saved_request.id)).info("Contact request received")
        return saved_request

    async def list_all(self, status: ContactRequestStatus | None = None) -> list[ContactRequest]:
        return await self._repository.list_all(status)

    async def get_by_id(self, contact_request_id: UUID) -> ContactRequest:
        contact_request = await self._repository.get_by_id(contact_request_id)
        if contact_request is None:
            raise ContactRequestNotFoundError
        return contact_request

    async def update_status(
        self, contact_request_id: UUID, status: ContactRequestStatus
    ) -> ContactRequest:
        contact_request = await self.get_by_id(contact_request_id)
        updated = ContactRequest(
            id=contact_request.id,
            name=contact_request.name,
            email_address=contact_request.email_address,
            company=contact_request.company,
            phone=contact_request.phone,
            service=contact_request.service,
            message=contact_request.message,
            status=status,
            created_at=contact_request.created_at,
            updated_at=self._clock(),
        )
        saved = await self._repository.update(updated)
        logger.bind(contact_request_id=str(saved.id), status=status.value).info(
            "Lead status updated"
        )
        return saved
