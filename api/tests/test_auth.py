from fastapi.testclient import TestClient


CREDENTIALS = {"email": "bob@exemple.fr", "password": "motdepasse"}


def test_register_returns_public_user(client: TestClient) -> None:
    response = client.post("/auth/register", json=CREDENTIALS)

    assert response.status_code == 201
    assert set(response.json()) == {"id", "email"}
    assert response.json()["email"] == "bob@exemple.fr"


def test_register_refuses_duplicate_email(client: TestClient) -> None:
    client.post("/auth/register", json=CREDENTIALS)
    response = client.post(
        "/auth/register",
        json={"email": "BOB@exemple.fr", "password": "motdepasse"},
    )

    assert response.status_code == 409
    assert response.json() == {
        "erreur": {"code": 409, "message": "Email déjà utilisé"}
    }


def test_register_requires_long_password(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "bob@exemple.fr", "password": "court"},
    )

    assert response.status_code == 422
    assert "password" in response.json()["erreur"]["message"]


def test_login_returns_bearer_token(client: TestClient) -> None:
    client.post("/auth/register", json=CREDENTIALS)
    response = client.post("/auth/login", json=CREDENTIALS)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    client.post("/auth/register", json=CREDENTIALS)
    response = client.post(
        "/auth/login",
        json={"email": "bob@exemple.fr", "password": "x"},
    )

    assert response.status_code == 401
    assert response.json()["erreur"]["code"] == 401


def test_me_returns_current_user(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == "alice@exemple.fr"


def test_me_without_token_returns_401(client: TestClient) -> None:
    assert client.get("/auth/me").status_code == 401


def test_me_with_invalid_token_returns_401(client: TestClient) -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer faux-token"},
    )

    assert response.status_code == 401
