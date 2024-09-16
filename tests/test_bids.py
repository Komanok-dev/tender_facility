from tests.utils import (
    create_test_organization,
    create_test_user,
    create_test_tender,
    assign_responsibility,
    create_test_bid,
)


def test_create_new_bid(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)

    response = client.post(
        "/api/token", data={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    bid_data = {
        "tender_id": str(test_tender.id),
        "description": "Test Bid Description",
        "price": 1000.00,
    }

    response = client.post(
        "/api/bids/new", json=bid_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test Bid Description"
    assert data["price"] == 1000.00


def test_publish_bid(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)

    test_bid = create_test_bid(db_session, test_tender.id, test_user.id)

    response = client.post(
        "/api/token", data={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.post(
        f"/api/bids/{test_bid.id}/publish", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PUBLISHED"


def test_cancel_bid(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)
    test_bid = create_test_bid(db_session, test_tender.id, test_user.id)

    response = client.post(
        "/api/token", data={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.post(
        f"/api/bids/{test_bid.id}/cancel", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CANCELED"


def test_edit_bid(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)
    test_bid = create_test_bid(db_session, test_tender.id, test_user.id)

    response = client.post(
        "/api/token", data={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    updated_data = {
        "tender_id": str(test_tender.id),
        "description": "Updated Bid Description",
        "price": 2000.00,
    }

    response = client.patch(
        f"/api/bids/{test_bid.id}/edit",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated Bid Description"
    assert data["price"] == 2000.00


def test_rollback_bid_version(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)

    assign_responsibility(db_session, test_organization.id, test_user.id)

    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)
    test_bid = create_test_bid(db_session, test_tender.id, test_user.id)

    response = client.post(
        "/api/token", data={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    updated_data = {
        "tender_id": str(test_tender.id),
        "description": "Updated Bid Description",
        "price": 2000.00,
    }
    response = client.patch(
        f"/api/bids/{test_bid.id}/edit",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = client.put(
        f"/api/bids/{test_bid.id}/rollback/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == 1


def test_approve_bid(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)
    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)
    test_bid = create_test_bid(db_session, test_tender.id, test_user.id)

    response = client.post(
        "/api/token", data={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.post(
        f"/api/bids/{test_bid.id}/approve", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED"
