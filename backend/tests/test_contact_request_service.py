from datetime import UTC, datetime
from itertools import count
from uuid import UUID

import pytest

from site_api.domain.contacts import ContactRequestNotFoundError, ContactRequestStatus
from site_api.services.contact_requests import (
    ContactRequestService,
    SubmitContactRequest,
)
from tests.conftest import InMemoryContactRequestRepository


@pytest.mark.asyncio
async def test_submit_builds_and_persists_contact_request(
    repository: InMemoryContactRequestRepository,
) -> None:
    expected_id = UUID("9a53d09a-f258-4b09-9fb3-ef6df4c2f9fd")
    expected_time = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)
    service = ContactRequestService(
        repository,
        id_factory=lambda: expected_id,
        clock=lambda: expected_time,
    )

    result = await service.submit(
        SubmitContactRequest(
            name="Taylor Client",
            email_address="taylor@example.com",
            company=None,
            phone=None,
            service="Asphalt Repair",
            message="Please call me.",
        )
    )

    assert result.id == expected_id
    assert result.created_at == expected_time
    assert result.updated_at == expected_time
    assert result.status is ContactRequestStatus.RECEIVED
    assert repository.contact_requests == [result]


def _submit_command(**overrides: object) -> SubmitContactRequest:
    defaults: dict[str, object] = {
        "name": "Taylor Client",
        "email_address": "taylor@example.com",
        "company": None,
        "phone": None,
        "service": "Website Redesign",
        "message": "Please call me.",
    }
    defaults.update(overrides)
    return SubmitContactRequest(**defaults)


@pytest.fixture
def service(repository: InMemoryContactRequestRepository) -> ContactRequestService:
    ids = iter(UUID(int=n) for n in count(1))
    return ContactRequestService(repository, id_factory=lambda: next(ids))


@pytest.mark.asyncio
async def test_list_all_filters_by_status(service: ContactRequestService) -> None:
    first = await service.submit(_submit_command())
    second = await service.submit(_submit_command(email_address="other@example.com"))
    await service.update_status(second.id, ContactRequestStatus.CONTACTED)

    received_only = await service.list_all(ContactRequestStatus.RECEIVED)
    contacted_only = await service.list_all(ContactRequestStatus.CONTACTED)

    assert [lead.id for lead in received_only] == [first.id]
    assert [lead.id for lead in contacted_only] == [second.id]


@pytest.mark.asyncio
async def test_get_by_id_raises_when_missing(service: ContactRequestService) -> None:
    with pytest.raises(ContactRequestNotFoundError):
        await service.get_by_id(UUID(int=999))


@pytest.mark.asyncio
async def test_update_status_moves_lead_through_pipeline(
    service: ContactRequestService,
) -> None:
    lead = await service.submit(_submit_command())

    contacted = await service.update_status(lead.id, ContactRequestStatus.CONTACTED)
    assert contacted.status is ContactRequestStatus.CONTACTED
    assert contacted.updated_at >= lead.created_at

    won = await service.update_status(lead.id, ContactRequestStatus.WON)
    assert won.status is ContactRequestStatus.WON
    assert won.created_at == lead.created_at


@pytest.mark.asyncio
async def test_update_status_raises_when_missing(service: ContactRequestService) -> None:
    with pytest.raises(ContactRequestNotFoundError):
        await service.update_status(UUID(int=999), ContactRequestStatus.LOST)
