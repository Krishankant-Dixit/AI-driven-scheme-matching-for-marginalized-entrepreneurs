from datetime import datetime, timezone

from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.routes import profile as profile_routes
from app.core.security import get_current_user
from app.schemas.profile import ProfileCreate
from app.services.profiles import create_profile, get_owned_profile


VALID_PROFILE = {
    "name": "Example User",
    "age": 24,
    "gender": "FEMALE",
    "category": "OBC",
    "state": "Uttar Pradesh",
    "district": "Hathras",
    "rural_urban": "RURAL",
    "business_name": "Example Foods",
    "business_type": "PROPRIETORSHIP",
    "business_sector": "FOOD_PROCESSING",
    "business_stage": "NEW",
    "business_description": "  Small food processing business  ",
    "annual_income": 250000,
    "investment_capacity": 300000,
    "loan_required": 500000,
}


class FakeInsertResult:
    def __init__(self, inserted_id: ObjectId):
        self.inserted_id = inserted_id


class FakeCollection:
    def __init__(self):
        self.document = None
        self.document_id = ObjectId()

    def insert_one(self, document):
        self.document = {**document, "_id": self.document_id}
        return FakeInsertResult(self.document_id)

    def create_index(self, *args, **kwargs):
        return "user_id"

    def find_one(self, query):
        if self.document and all(self.document.get(key) == value for key, value in query.items()):
            return self.document
        return None


def make_client(monkeypatch):
    collection = FakeCollection()
    monkeypatch.setattr(profile_routes, "_profiles_collection", lambda: collection)
    app.dependency_overrides[get_current_user] = lambda: {"_id": ObjectId("65f1c9e8b8d2a123456789ab"), "is_active": True}
    client = TestClient(app)
    return client, collection


def test_valid_profile_creation(monkeypatch):
    client, collection = make_client(monkeypatch)

    response = client.post("/api/profile", json=VALID_PROFILE)

    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["profile"]["business_description"] == "Small food processing business"
    assert collection.document["loan_required"] == 500000.0


def test_missing_required_fields_are_rejected(monkeypatch):
    client, _ = make_client(monkeypatch)

    for field in ("name", "state", "district"):
        payload = {key: value for key, value in VALID_PROFILE.items() if key != field}
        response = client.post("/api/profile", json=payload)
        assert response.status_code == 422


def test_invalid_age_and_negative_financial_values_are_rejected(monkeypatch):
    client, _ = make_client(monkeypatch)

    for field, value in (("age", 121), ("annual_income", -1), ("investment_capacity", -1), ("loan_required", -1)):
        payload = {**VALID_PROFILE, field: value}
        response = client.post("/api/profile", json=payload)
        assert response.status_code == 422


def test_optional_fields_and_unknown_values_are_preserved(monkeypatch):
    client, collection = make_client(monkeypatch)
    payload = {
        "name": "Unknown Details",
        "state": "Karnataka",
        "district": "Mysuru",
        "gender": "UNKNOWN",
        "category": "UNKNOWN",
        "rural_urban": "UNKNOWN",
        "business_stage": "UNKNOWN",
    }

    response = client.post("/api/profile", json=payload)

    assert response.status_code == 201
    assert collection.document["annual_income"] is None
    assert response.json()["profile"]["gender"] == "UNKNOWN"
    assert response.json()["profile"]["loan_required"] is None


def test_successful_profile_retrieval(monkeypatch):
    client, _ = make_client(monkeypatch)
    created = client.post("/api/profile", json=VALID_PROFILE)

    response = client.get(f"/api/profile/{created.json()['profile_id']}")

    assert response.status_code == 200
    assert response.json()["profile"]["name"] == "Example User"


def test_profile_not_found_and_invalid_id(monkeypatch):
    client, _ = make_client(monkeypatch)

    assert client.get(f"/api/profile/{ObjectId()}").status_code == 404
    assert client.get("/api/profile/not-an-object-id").status_code == 400


def test_two_users_cannot_read_each_others_profiles():
    collection = FakeCollection()
    profile = ProfileCreate(name="Owner A", state="State A", district="District A")
    created = create_profile(collection, profile, "user-a")

    assert get_owned_profile(collection, created.profile_id, "user-a") is not None
    assert get_owned_profile(collection, created.profile_id, "user-b") is None
