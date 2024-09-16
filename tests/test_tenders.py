from tests.utils import create_test_organization, create_test_user, create_test_tender, assign_responsibility

def test_get_tenders(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    create_test_tender(db_session, test_organization.id, test_user.id)
    create_test_tender(db_session, test_organization.id, test_user.id)

    response = client.post("/api/token", data={"username": test_user.username, "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get("/api/tenders", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    tenders = response.json()
    
    assert isinstance(tenders, list)
    assert len(tenders) > 0


def test_create_new_tender(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    response = client.post("/api/token", data={"username": test_user.username, "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    tender_data = {
        "title": "New Tender",
        "description": "New Tender Description",
        "serviceType": "Construction"
    }

    response = client.post(
        "/api/tenders/new",
        json=tender_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["description"] == "Тендер успешно создан."

def test_get_user_tenders(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    create_test_tender(db_session, test_organization.id, test_user.id)
    create_test_tender(db_session, test_organization.id, test_user.id)

    response = client.post("/api/token", data={"username": test_user.username, "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get("/api/tenders/my", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert len(data["data"]["tenders"]) > 0


def test_publish_tender(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)

    response = client.post("/api/token", data={"username": test_user.username, "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.patch(f"/api/tenders/{test_tender.id}/publish", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["description"] == "Тендер успешно опубликован."

def test_close_tender(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)

    response = client.post("/api/token", data={"username": test_user.username, "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.post(f"/api/tenders/{test_tender.id}/close", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["description"] == "Тендер успешно закрыт."


def test_edit_tender(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)

    response = client.post("/api/token", data={"username": test_user.username, "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    updated_data = {
        "title": "Обновленный тендер",
        "description": "Обновленное описание",
        "serviceType": "Delivery"
    }

    response = client.patch(f"/api/tenders/{test_tender.id}/edit", json=updated_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["name"] == "Обновленный тендер"
    assert data["data"]["description"] == "Обновленное описание"


def test_rollback_tender_version(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)

    response = client.post("/api/token", data={"username": test_user.username, "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    updated_data = {
        "title": "Updated Tender",
        "description": "Updated Description",
        "serviceType": "Delivery"
    }
    response = client.patch(f"/api/tenders/{test_tender.id}/edit", json=updated_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = client.put(f"/api/tenders/{test_tender.id}/rollback/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["description"] == "Тендер успешно откатан до версии."
    assert data["data"]["version"] == 1
