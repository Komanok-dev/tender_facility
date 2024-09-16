import uuid
from backend.auth import get_password_hash
from backend.models import Organization, Employee, Tender, OrganizationResponsible, Bid, BidReview

def create_test_organization(db):
    organization = Organization(
        id=uuid.uuid4(),
        name="Test Organization",
        description="Description of test organization",
        type="LLC",
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization

def create_test_user(db, organization_id, username="test_user"):
    hashed_password = get_password_hash("password")
    user = Employee(
        username=username,
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
        organization_id=organization_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_tender(db, organization_id, responsible_user_id):
    tender = Tender(
        title="Test Tender",
        description="Test Tender Description",
        serviceType="Construction",
        version=1,
        status="CREATED",
        organization_id=organization_id,
        responsible_user_id=responsible_user_id,
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)
    return tender

def assign_responsibility(db, organization_id, user_id):
    responsible = OrganizationResponsible(
        organization_id=organization_id,
        user_id=user_id
    )
    db.add(responsible)
    db.commit()
    db.refresh(responsible)
    return responsible

def create_test_bid(db, tender_id, author_id):
    bid = Bid(
        id=uuid.uuid4(),
        tender_id=tender_id,
        author_id=author_id,
        description="Test Bid Description",
        price=1000.00,
        version=1,
        status="CREATED"
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)
    print(f"Создано предложение: {bid.id} для тендера {tender_id} и автора {author_id}")
    return bid

def create_test_review(db_session, bid_id, reviewer_id, review, status):
    bid_review = BidReview(
        bid_id=bid_id,
        reviewer_id=reviewer_id,
        review=review,
        status=status
    )
    db_session.add(bid_review)
    db_session.commit()
    db_session.refresh(bid_review)
    print(f"Создан отзыв: {bid_review.id} для предложения {bid_id} от рецензента {reviewer_id}")
    return bid_review
