from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from loguru import logger

from site_api.domain.contacts import (
    ContactRequest,
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
        contact_request = ContactRequest(
            id=self._id_factory(),
            name=command.name,
            email_address=command.email_address,
            company=command.company,
            phone=command.phone,
            service=command.service,
            message=command.message,
            status=ContactRequestStatus.RECEIVED,
            created_at=self._clock(),
        )
        saved_request = await self._repository.add(contact_request)
        logger.bind(contact_request_id=str(saved_request.id)).info("Contact request received")
        return saved_request
