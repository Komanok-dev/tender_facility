from pydantic import BaseModel, ConfigDict, UUID4
from enum import Enum
from typing import Optional
from datetime import datetime


class BaseResponse(BaseModel):
    success: bool
    description: Optional[str] = None
    data: Optional[dict] = None


class OrganizationType(str, Enum):
    IE = "IE"
    LLC = "LLC"
    JSC = "JSC"


class TenderStatus(str, Enum):
    CREATED = "CREATED"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"


class BidStatus(str, Enum):
    CREATED = "CREATED"
    PUBLISHED = "PUBLISHED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"


class EmployeeBase(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    username: str
    hashed_password: str


class EmployeeResponse(EmployeeBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: OrganizationType


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationResponsibleBase(BaseModel):
    organization_id: UUID4
    user_id: UUID4


class OrganizationResponsibleCreate(OrganizationResponsibleBase):
    pass


class OrganizationResponsibleResponse(OrganizationResponsibleBase):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)


class TenderCreate(BaseModel):
    title: str
    description: str
    serviceType: str


class TenderResponse(BaseResponse):
    pass


class BidCreate(BaseModel):
    tender_id: UUID4
    description: Optional[str] = None
    price: float


class BidResponse(BaseModel):
    id: UUID4
    tender_id: UUID4
    price: float
    description: Optional[str]
    author_id: UUID4
    status: str
    created_at: datetime
    updated_at: datetime
    version: int

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    id: str


class Token(BaseModel):
    access_token: str
    token_type: str


class BidReviewBase(BaseModel):
    review: Optional[str] = None
    status: BidStatus


class BidReviewCreate(BidReviewBase):
    pass


class BidReviewResponse(BidReviewBase):
    id: UUID4
    bid_id: UUID4
    reviewer_id: UUID4

    model_config = ConfigDict(from_attributes=True)
