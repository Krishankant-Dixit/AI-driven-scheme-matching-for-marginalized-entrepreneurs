from datetime import datetime, timezone

from bson import ObjectId
from fastapi.testclient import TestClient

from app.core import security
from app.main import app
from app.routes import auth as auth_routes


class FakeCollection:
    def __init__(self):
        self.documents = []

    def create_index(self, *args, **kwargs):
        return "index"

    def insert_one(self, document):
        document = {**document, "_id": ObjectId()}
        self.documents.append(document)
        return type("Result", (), {"inserted_id": document["_id"]})()

    def find_one(self, query):
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return document
        return None

    def update_one(self, query, update):
        document = self.find_one(query)
        if document:
            document.update(update.get("$set", {}))


class FakeDatabase:
    def __init__(self):
        self.collections = {"users": FakeCollection()}

    def __getitem__(self, name):
        return self.collections.setdefault(name, FakeCollection())


def test_registration_login_and_me(monkeypatch):
    database = FakeDatabase()
    monkeypatch.setattr(auth_routes, "get_database", lambda: database)
    monkeypatch.setattr(security, "get_database", lambda: database)
    client = TestClient(app)

    registered = client.post("/api/auth/register", json={"name": "User One", "email": " User@Example.COM ", "password": "strong-password"})
    assert registered.status_code == 201
    assert "password_hash" not in registered.text

    logged_in = client.post("/api/auth/login", json={"email": "user@example.com", "password": "strong-password"})
    assert logged_in.status_code == 200
    token = logged_in.json()["access_token"]
    assert "password_hash" not in logged_in.text

    current = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert current.status_code == 200
    assert current.json()["email"] == "user@example.com"


def test_duplicate_email_and_bad_credentials(monkeypatch):
    database = FakeDatabase()
    monkeypatch.setattr(auth_routes, "get_database", lambda: database)
    client = TestClient(app)
    payload = {"name": "User One", "email": "user@example.com", "password": "strong-password"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/login", json={"email": payload["email"], "password": "wrong-password"}).status_code == 401


def test_missing_and_invalid_tokens_are_rejected():
    client = TestClient(app)
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401