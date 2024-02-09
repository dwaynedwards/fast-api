import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..database import get_session
from ..main import app
from ..models.item import Item


@pytest.fixture(name="session")
def get_session_fixture():
    DATABASE_URL = "sqlite://"
    connect_args = {"check_same_thread": False}

    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args=connect_args,
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Create Item Tests


def test_create_item(client: TestClient):
    response = client.post("/items/", json={"name": "Apple"})
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED, response.text

    assert data["id"] is not None
    assert data["name"] == "Apple"


def test_create_hero_incomplete(client: TestClient):
    # No name
    response = client.post("/items/", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text


def test_create_hero_invalid(client: TestClient):
    # name has an invalid type
    response = client.post("/items/", json={"name": ["Apple"]})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text


# Read Items Tests


def test_read_items_no_items(client: TestClient):
    response = client.get("/items/")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK, response.text
    assert data == []


def test_read_items(session: Session, client: TestClient):
    item_1 = Item(name="Apple")
    item_2 = Item(name="Orange")
    session.add(item_1)
    session.add(item_2)
    session.commit()

    response = client.get("/items/")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK, response.text

    assert len(data) == 2
    assert data[0]["id"] == item_1.id
    assert data[0]["name"] == item_1.name
    assert data[1]["id"] == item_2.id
    assert data[1]["name"] == item_2.name


# Read Item Tests


def test_read_item(session: Session, client: TestClient):
    item_1 = Item(name="Apple")
    session.add(item_1)
    session.commit()

    response = client.get(f"/items/{item_1.id}")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK, response.text

    assert data["id"] == item_1.id
    assert data["name"] == item_1.name


def test_read_item_no_found(session: Session, client: TestClient):
    session.add(Item(name="Apple"))
    session.commit()

    fake_item_id = 0
    response = client.get(f"/items/{fake_item_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text


# Update Item Tests


def test_update_item(session: Session, client: TestClient):
    item_1 = Item(name="Apple")
    session.add(item_1)
    session.commit()

    update_item_name = "Orange"
    response = client.patch(f"/items/{item_1.id}", json={"name": update_item_name})
    data = response.json()

    assert response.status_code == status.HTTP_200_OK, response.text

    assert data["id"] == item_1.id
    assert data["name"] == update_item_name


def test_update_item_not_updated(session: Session, client: TestClient):
    item_1 = Item(name="Apple")
    session.add(item_1)
    session.commit()

    # No name
    response = client.patch(f"/items/{item_1.id}", json={})

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text


def test_update_item_no_found(session: Session, client: TestClient):
    session.add(Item(name="Apple"))
    session.commit()

    fake_item_id = 0
    response = client.patch(f"/items/{fake_item_id}", json={})

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text


# Delete Item Tests


def test_delete_item(session: Session, client: TestClient):
    item_1 = Item(name="Apple")
    session.add(item_1)
    session.commit()

    response = client.delete(f"/items/{item_1.id}")

    db_item = session.get(Item, item_1.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

    assert db_item is None


def test_delete_item_no_found(session: Session, client: TestClient):
    session.add(Item(name="Apple"))
    session.commit()

    fake_item_id = 0
    response = client.delete(f"/items/{fake_item_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
