from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient


def add_entry(
    client: TestClient,
    headers: dict[str, str],
    item_id: int,
    statut: str = "a_decouvrir",
    note: int | None = None,
) -> dict[str, Any]:
    response = client.post(
        "/me/collection",
        json={"item_id": item_id, "statut": statut, "note": note},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_collection_requires_token(client: TestClient) -> None:
    assert client.get("/me/collection").status_code == 401
    assert client.get("/me/stats").status_code == 401


def test_add_entry_returns_nested_item(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    entry = add_entry(client, auth_headers, item_id=1, statut="en_cours", note=4)

    assert entry["statut"] == "en_cours"
    assert entry["note"] == 4
    assert entry["commentaire"] is None
    assert str(entry["date_ajout"]).endswith("Z")
    assert entry["item"]["id"] == 1


def test_note_is_optional(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    entry = add_entry(client, auth_headers, item_id=1)

    assert entry["note"] is None


def test_same_item_cannot_be_added_twice(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    add_entry(client, auth_headers, item_id=1)
    response = client.post(
        "/me/collection",
        json={"item_id": 1, "statut": "termine"},
        headers=auth_headers,
    )

    assert response.status_code == 409


def test_add_unknown_item_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/me/collection",
        json={"item_id": 999, "statut": "termine"},
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_add_entry_validates_statut_and_note(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    bad_statut = {"item_id": 1, "statut": "fini"}
    bad_note = {"item_id": 1, "statut": "termine", "note": 6}

    assert client.post("/me/collection", json=bad_statut, headers=auth_headers).status_code == 422
    assert client.post("/me/collection", json=bad_note, headers=auth_headers).status_code == 422


def test_filter_and_sort_collection(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    add_entry(client, auth_headers, item_id=1, statut="termine", note=2)
    add_entry(client, auth_headers, item_id=2, statut="en_cours", note=5)
    add_entry(client, auth_headers, item_id=3, statut="termine", note=4)

    finished = client.get(
        "/me/collection",
        params={"statut": "termine"},
        headers=auth_headers,
    ).json()
    sorted_by_note = client.get(
        "/me/collection",
        params={"tri": "note"},
        headers=auth_headers,
    ).json()

    assert {entry["item"]["id"] for entry in finished} == {1, 3}
    assert [entry["note"] for entry in sorted_by_note] == [5, 4, 2]


def test_update_entry(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    entry = add_entry(client, auth_headers, item_id=1, note=3)
    response = client.patch(
        f"/me/collection/{entry['id']}",
        json={"statut": "termine", "commentaire": "Excellent"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["statut"] == "termine"
    assert response.json()["commentaire"] == "Excellent"
    assert response.json()["note"] == 3


def test_update_refuses_null_statut(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    entry = add_entry(client, auth_headers, item_id=1)
    response = client.patch(
        f"/me/collection/{entry['id']}",
        json={"statut": None},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_delete_entry(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    entry = add_entry(client, auth_headers, item_id=1)
    url = f"/me/collection/{entry['id']}"

    response = client.delete(url, headers=auth_headers)

    assert response.status_code == 204
    assert response.content == b""
    assert client.delete(url, headers=auth_headers).status_code == 404


def test_user_cannot_touch_another_user_entry(
    client: TestClient,
    auth_headers: dict[str, str],
    create_user: Callable[[str], dict[str, str]],
) -> None:
    entry = add_entry(client, auth_headers, item_id=1)
    other_headers = create_user("bob@exemple.fr")
    url = f"/me/collection/{entry['id']}"

    assert client.get("/me/collection", headers=other_headers).json() == []
    assert client.patch(url, json={"note": 1}, headers=other_headers).status_code == 404
    assert client.delete(url, headers=other_headers).status_code == 404


def test_stats(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    add_entry(client, auth_headers, item_id=1, statut="termine", note=4)
    add_entry(client, auth_headers, item_id=2, statut="termine", note=5)
    add_entry(client, auth_headers, item_id=3, statut="en_cours")

    response = client.get("/me/stats", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "total": 3,
        "par_statut": {"a_decouvrir": 0, "en_cours": 1, "termine": 2},
        "note_moyenne": 4.5,
    }


def test_stats_of_empty_collection(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get("/me/stats", headers=auth_headers)

    assert response.json() == {
        "total": 0,
        "par_statut": {"a_decouvrir": 0, "en_cours": 0, "termine": 0},
        "note_moyenne": None,
    }
