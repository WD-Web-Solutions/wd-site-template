from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from site_api.api.dependencies import get_contact_request_service, require_admin
from site_api.domain.contacts import (
    ContactRequest,
    ContactRequestNotFoundError,
    ContactRequestStatus,
)
from site_api.services.contact_requests import ContactRequestService

router = APIRouter(
    prefix="/admin/contact-requests",
    tags=["admin contact requests"],
    dependencies=[Depends(require_admin)],
)


class LeadDetail(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: UUID
    name: str
    email_address: str
    company: str | None
    phone: str | None
    service: str
    message: str
    status: ContactRequestStatus
    created_at: datetime
    updated_at: datetime


class UpdateStatusRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    status: ContactRequestStatus


def to_lead_detail(contact_request: ContactRequest) -> LeadDetail:
    return LeadDetail(
        id=contact_request.id,
        name=contact_request.name,
        email_address=contact_request.email_address,
        company=contact_request.company,
        phone=contact_request.phone,
        service=contact_request.service,
        message=contact_request.message,
        status=contact_request.status,
        created_at=contact_request.created_at,
        updated_at=contact_request.updated_at,
    )


@router.get("", response_model=list[LeadDetail], response_model_by_alias=True)
async def list_leads(
    service: Annotated[ContactRequestService, Depends(get_contact_request_service)],
    status_filter: Annotated[ContactRequestStatus | None, Query(alias="status")] = None,
) -> list[LeadDetail]:
    leads = await service.list_all(status_filter)
    return [to_lead_detail(lead) for lead in leads]


@router.patch(
    "/{contact_request_id}/status",
    response_model=LeadDetail,
    response_model_by_alias=True,
)
async def update_lead_status(
    contact_request_id: UUID,
    payload: UpdateStatusRequest,
    service: Annotated[ContactRequestService, Depends(get_contact_request_service)],
) -> LeadDetail:
    try:
        lead = await service.update_status(contact_request_id, payload.status)
    except ContactRequestNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        ) from error

    return to_lead_detail(lead)
