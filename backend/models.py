import uuid
import enum
from sqlalchemy import Column, String, Integer, Text, Enum, ForeignKey, TIMESTAMP, func, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class OrganizationType(enum.Enum):
    IE = "IE"
    LLC = "LLC"
    JSC = "JSC"


class TenderStatus(enum.Enum):
    CREATED = "CREATED"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"


class BidStatus(enum.Enum):
    CREATED = "CREATED"
    PUBLISHED = "PUBLISHED"
    CANCELED = "CANCELED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Employee(Base):
    __tablename__ = "employee"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    tenders = relationship("Tender", back_populates="responsible_user")
    bids = relationship("Bid", back_populates="author")
    bid_reviews = relationship("BidReview", back_populates="reviewer")
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organization.id'))
    

class Organization(Base):
    __tablename__ = "organization"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(OrganizationType))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    tenders = relationship("Tender", back_populates="organization")


class OrganizationResponsible(Base):
    __tablename__ = "organization_responsible"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organization.id", ondelete="CASCADE")
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("employee.id", ondelete="CASCADE"))


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(String)
    serviceType = Column(String(100))
    version = Column(Integer, default=1)
    status = Column(Enum(TenderStatus), default=TenderStatus.CREATED)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))
    responsible_user_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    organization = relationship("Organization", back_populates="tenders")
    responsible_user = relationship("Employee", back_populates="tenders")
    bids = relationship("Bid", back_populates="tender")


class Bid(Base):
    __tablename__ = "bid"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"))
    version = Column(Integer, default=1)
    status = Column(Enum(BidStatus), default=BidStatus.CREATED)
    price = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    tender = relationship("Tender", back_populates="bids")
    author = relationship("Employee", back_populates="bids")
    reviews = relationship("BidReview", back_populates="bid")


class BidReview(Base):
    __tablename__ = "bid_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bid_id = Column(UUID(as_uuid=True), ForeignKey("bid.id"))
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"))
    review = Column(Text, nullable=True)
    status = Column(Enum(BidStatus), default=BidStatus.CREATED)
    previous_version = Column(Integer, nullable=True)

    bid = relationship("Bid", back_populates="reviews")
    reviewer = relationship("Employee", back_populates="bid_reviews")
