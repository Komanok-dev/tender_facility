from tests.utils import (
    create_test_organization,
    create_test_user,
    create_test_tender,
    assign_responsibility,
    create_test_bid,
)


def test_add_review_to_bid(client, db_session):
    test_organization = create_test_organization(db_session)
    test_user = create_test_user(db_session, test_organization.id)
    test_tender = create_test_tender(db_session, test_organization.id, test_user.id)
    test_bid = create_test_bid(db_session, test_tender.id, test_user.id)

    response = client.post(
        "/api/token", data={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    review_data = {"review": "This is a test review", "status": "APPROVED"}

    response = client.post(
        f"/api/bids/{test_bid.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["review"] == "This is a test review"
    assert data["status"] == "APPROVED"


def test_get_reviews_for_bid(client, db_session):
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

    review_data = {"review": "Great bid!", "status": "APPROVED"}
    client.post(
        f"/api/bids/{test_bid.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/api/bids/{test_bid.id}/reviews", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["review"] == "Great bid!"
