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
