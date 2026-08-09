from datetime import UTC, datetime
from uuid import UUID

import pytest

from site_api.domain.contacts import ContactRequestStatus
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
    assert result.status is ContactRequestStatus.RECEIVED
    assert repository.contact_requests == [result]
