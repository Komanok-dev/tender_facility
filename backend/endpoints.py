from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
from datetime import timedelta
from .models import Tender, Bid, OrganizationResponsible, Employee, BidReview
from .schemas import (
    TenderCreate,
    TenderResponse,
    BidCreate,
    BidResponse,
    BidStatus,
    TenderStatus,
    BidReviewResponse,
    BidReviewCreate,
)

from .database import get_db
from .dependencies import get_current_user
from .auth import (
    create_access_token,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash,
)
from .schemas import Token

router = APIRouter(prefix="/api", tags=["API"])


@router.post("/register_user")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    new_user = Employee(username=username, hashed_password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id


@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/ping")
def ping():
    return "OK"


@router.get(
    "/tenders",
    summary="Получение списка тендеров",
    description="Список тендеров с возможностью фильтрации по типу услуг.",
)
def getTenders(
    service_type: Optional[str] = Query(None, alias="serviceType"),
    db: Session = Depends(get_db),
):
    query = db.query(Tender).order_by(Tender.title)
    if service_type:
        query = query.filter(Tender.serviceType == service_type)
    tenders = query.all()
    return tenders


@router.post(
    "/tenders/new",
    response_model=TenderResponse,
    summary="Создание нового тендера",
    description="Создание нового тендера с заданными параметрами.",
)
def createTender(
    tender: TenderCreate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    responsible = (
        db.query(OrganizationResponsible)
        .filter_by(
            organization_id=current_user.organization_id, user_id=current_user.id
        )
        .first()
    )
    if not responsible:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для выполнения действия."
        )

    new_tender = Tender(
        **tender.model_dump(),
        organization_id=current_user.organization_id,
        responsible_user_id=current_user.id,
        status="CREATED",
        version=1,
    )
    db.add(new_tender)
    db.commit()
    db.refresh(new_tender)
    response = TenderResponse(
        success=True,
        description="Тендер успешно создан.",
        data={"id": new_tender.id, "created_at": new_tender.created_at},
    )
    return response


@router.patch(
    "/tenders/{tender_id}/publish",
    response_model=TenderResponse,
    summary="Публикация тендера",
    description="Публикация тендера с заданными параметрами.",
)
def publish_tender(
    tender_id: str,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tender = db.query(Tender).filter_by(id=tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Тендер не найден.")
    if tender.responsible_user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для выполнения действия."
        )
    tender.status = "PUBLISHED"
    db.commit()
    db.refresh(tender)
    response = TenderResponse(
        success=True,
        description="Тендер успешно опубликован.",
        data={"id": tender.id, "created_at": tender.status},
    )
    return response


@router.get(
    "/tenders/my",
    summary="Получить тендеры пользователя",
    description="Получение списка тендеров текущего пользователя.",
    response_model=TenderResponse,
)
def getUserTenders(
    username: Optional[str] = Query(None),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if username:
        user = db.query(Employee).filter_by(username=username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не существует или некорректен.",
            )
    else:
        user = current_user

    tenders = (
        db.query(Tender)
        .filter_by(responsible_user_id=user.id)
        .order_by(Tender.title)
        .all()
    )

    return TenderResponse(
        success=True,
        description=f"Список тендеров пользователя {user.username} успешно получен.",
        data={
            "tenders": [
                {"id": tender.id, "title": tender.title, "status": tender.status}
                for tender in tenders
            ]
        },
    )


@router.post(
    "/tenders/{tender_id}/close",
    response_model=TenderResponse,
    summary="Закрытие тендера",
    description="Тендер успешно закрыт.",
)
def close_tender(
    tender_id: str,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tender = db.query(Tender).filter_by(id=tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Тендер не найден.")
    if tender.responsible_user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для выполнения действия."
        )
    tender.status = "CLOSED"
    db.commit()
    db.refresh(tender)
    response = TenderResponse(
        success=True,
        description="Тендер успешно закрыт.",
        data={"id": tender.id, "created_at": tender.status},
    )
    return response


@router.patch(
    "/tenders/{tender_id}/edit",
    response_model=TenderResponse,
    summary="Редактирование тендера",
    description="Изменение параметров существующего тендера.",
)
def editTender(
    tender_id: str,
    tender_data: TenderCreate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не существует или некорректен.",
        )

    tender = db.query(Tender).filter_by(id=tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тендер не найден."
        )

    if tender.responsible_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения действия.",
        )

    if not tender_data.title or not tender_data.description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Данные неправильно сформированы или не соответствуют требованиям.",
        )

    tender.title = tender_data.title
    tender.description = tender_data.description
    tender.version += 1
    db.commit()
    db.refresh(tender)

    return TenderResponse(
        success=True,
        description="Тендер успешно отредактирован.",
        data={"id": tender.id, "name": tender.title, "description": tender.description},
    )


@router.put(
    "/tenders/{tender_id}/rollback/{version}",
    response_model=TenderResponse,
    summary="Откат версии тендера",
    description="Откатить параметры тендера к указанной версии. Это считается новой правкой, поэтому версия инкрементируется.",
)
def rollback_tender(
    tender_id: str,
    version: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не существует или некорректен.",
        )

    tender = db.query(Tender).filter_by(id=tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Тендер или версия не найдены.")

    if current_user.id != tender.responsible_user_id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для выполнения действия."
        )

    if version <= 0:
        raise HTTPException(status_code=400, detail="Версия должна быть больше 0.")

    if version >= tender.version:
        raise HTTPException(
            status_code=400, detail="Новая версия должна быть меньше текущей версии."
        )

    tender.version = version
    db.commit()
    db.refresh(tender)

    return TenderResponse(
        success=True,
        description="Тендер успешно откатан до версии.",
        data={"id": tender.id, "version": tender.version},
    )


@router.post(
    "/bids/new",
    response_model=BidResponse,
    summary="Создание нового предложения",
    description="Создание предложения для существующего тендера.",
)
def create_bid(
    bid: BidCreate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tender = db.query(Tender).filter_by(id=bid.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    responsible = (
        db.query(OrganizationResponsible)
        .filter_by(
            organization_id=current_user.organization_id, user_id=current_user.id
        )
        .first()
    )

    if not responsible:
        raise HTTPException(
            status_code=403, detail="User is not responsible for the organization"
        )

    new_bid = Bid(
        tender_id=bid.tender_id,
        price=bid.price,
        description=bid.description,
        author_id=current_user.id,
        status="CREATED",
        version=1,
    )
    db.add(new_bid)
    db.commit()
    db.refresh(new_bid)

    return new_bid


@router.post("/bids/{bid_id}/publish", response_model=BidResponse)
def publish_bid(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    bid = db.query(Bid).filter_by(id=bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if (
        current_user.id != bid.author_id
        and current_user.organization_id != bid.tender.organization_id
    ):
        raise HTTPException(
            status_code=403, detail="You are not allowed to publish this bid"
        )
    bid.status = "PUBLISHED"
    db.commit()
    db.refresh(bid)
    return bid


@router.post("/bids/{bid_id}/cancel", response_model=BidResponse)
def cancel_bid(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    bid = db.query(Bid).filter_by(id=bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if (
        current_user.id != bid.author_id
        and current_user.organization_id != bid.tender.organization_id
    ):
        raise HTTPException(
            status_code=403, detail="You are not allowed to cancel this bid"
        )
    bid.status = "CANCELED"
    db.commit()
    db.refresh(bid)
    return bid


@router.patch("/bids/{bid_id}/edit", response_model=BidResponse)
def edit_bid(
    bid_id: str,
    bid_update: BidCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    bid = db.query(Bid).filter_by(id=bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if (
        current_user.id != bid.author_id
        and current_user.organization_id != bid.tender.organization_id
    ):
        raise HTTPException(
            status_code=403, detail="You are not allowed to edit this bid"
        )
    bid.description = bid_update.description
    bid.price = bid_update.price
    bid.version += 1
    bid.tender_id = bid_update.tender_id
    db.commit()
    db.refresh(bid)
    return bid


@router.post("/bids/{bid_id}/approve", response_model=BidResponse)
def approve_bid(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    bid = db.query(Bid).filter_by(id=bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    if current_user.organization_id != bid.tender.organization_id:
        raise HTTPException(
            status_code=403,
            detail="You are not responsible for this tender's organization",
        )

    reviews = db.query(BidReview).filter_by(bid_id=bid_id).all()
    if any(review.status == BidStatus.REJECTED for review in reviews):
        bid.status = BidStatus.REJECTED
    else:
        quorum = min(
            3,
            len(
                db.query(OrganizationResponsible)
                .filter_by(organization_id=bid.tender.organization_id)
                .all()
            ),
        )
        if (
            len([review for review in reviews if review.status == BidStatus.APPROVED])
            >= quorum
        ):
            bid.status = BidStatus.APPROVED
            bid.tender.status = TenderStatus.CLOSED
    db.commit()
    db.refresh(bid)
    return bid


@router.post("/bids/{bid_id}/review", response_model=BidReviewResponse)
def add_review(
    bid_id: str,
    review: BidReviewCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    bid = db.query(Bid).filter_by(id=bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if current_user.organization_id != bid.tender.organization_id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to review this bid"
        )
    existing_review = (
        db.query(BidReview)
        .filter_by(bid_id=bid_id, reviewer_id=current_user.id)
        .first()
    )
    if existing_review:
        raise HTTPException(
            status_code=400, detail="You have already reviewed this bid"
        )
    new_review = BidReview(
        bid_id=bid_id,
        reviewer_id=current_user.id,
        review=review.review,
        status=review.status,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


@router.get("/bids/{bid_id}/reviews", response_model=List[BidReviewResponse])
def get_reviews(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    bid = db.query(Bid).filter_by(id=bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if current_user.organization_id != bid.tender.organization_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view reviews for this bid",
        )
    reviews = db.query(BidReview).filter_by(bid_id=bid_id).all()
    return reviews


@router.put("/bids/{bid_id}/rollback/{version}", response_model=BidResponse)
def rollback_bid(
    bid_id: str,
    version: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    bid = db.query(Bid).filter_by(id=bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    if current_user.id != bid.author_id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to rollback this bid"
        )
    if version <= 0:
        raise HTTPException(status_code=400, detail="Version must be greater than 0")
    if version >= bid.version:
        raise HTTPException(
            status_code=400,
            detail="Cannot rollback to a version greater or equal to the current version",
        )

    bid.version = version
    db.commit()
    db.refresh(bid)
    return bid


@router.get("/bids/{tender_id}/reviews", response_model=List[BidReviewResponse])
def get_reviews_for_tender(
    tender_id: str,
    author_username: str,
    organization_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    if str(current_user.organization_id) != str(organization_id):
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для просмотра отзывов."
        )

    author = db.query(Employee).filter_by(username=author_username).first()
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден.")

    bids = (
        db.query(Bid)
        .filter(Bid.author_id == author.id, Bid.tender_id == tender_id)
        .all()
    )

    if not bids:
        raise HTTPException(status_code=404, detail="Предложения автора не найдены.")

    reviews = (
        db.query(BidReview)
        .filter(BidReview.bid_id.in_([str(bid.id) for bid in bids]))
        .all()
    )

    if not reviews:
        raise HTTPException(status_code=404, detail="Отзывы не найдены.")

    return reviews
