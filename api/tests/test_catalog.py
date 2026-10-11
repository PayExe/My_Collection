from fastapi.testclient import TestClient

from api.seed import seed_catalog


def test_items_uses_default_pagination(client: TestClient) -> None:
    response = client.get("/items")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 40
    assert body["page"] == 1
    assert body["limit"] == 12
    assert len(body["results"]) == 12


def test_item_has_contract_fields(client: TestClient) -> None:
    item = client.get("/items").json()["results"][0]

    assert set(item) == {
        "id",
        "titre",
        "categorie",
        "description",
        "image_url",
        "annee",
        "studio",
        "plateforme",
    }


def test_items_search_by_keyword(client: TestClient) -> None:
    body = client.get("/items", params={"q": "zelda"}).json()

    assert body["total"] == 2
    assert all("Zelda" in item["titre"] for item in body["results"])


def test_items_filter_by_category(client: TestClient) -> None:
    body = client.get("/items", params={"categorie": "RPG", "limit": 50}).json()

    assert body["total"] > 0
    assert all(item["categorie"] == "RPG" for item in body["results"])


def test_items_validates_query_parameters(client: TestClient) -> None:
    assert client.get("/items", params={"q": "a"}).status_code == 422
    assert client.get("/items", params={"page": 0}).status_code == 422
    assert client.get("/items", params={"limit": 51}).status_code == 422


def test_item_detail(client: TestClient) -> None:
    response = client.get("/items/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_unknown_item_returns_404_with_error_format(client: TestClient) -> None:
    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json() == {
        "erreur": {"code": 404, "message": "Jeu introuvable"}
    }


def test_seed_can_run_twice_without_duplicates(client: TestClient) -> None:
    client.portal.call(seed_catalog)

    assert client.get("/items").json()["total"] == 40
