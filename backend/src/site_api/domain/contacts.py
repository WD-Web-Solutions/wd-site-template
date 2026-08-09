from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class ContactRequestStatus(StrEnum):
    RECEIVED = "received"


@dataclass(frozen=True, slots=True)
class ContactRequest:
    id: UUID
    name: str
    email_address: str
    company: str | None
    phone: str | None
    service: str
    message: str
    status: ContactRequestStatus
    created_at: datetime


class ContactRequestRepository(Protocol):
    async def add(self, contact_request: ContactRequest) -> ContactRequest: ...
