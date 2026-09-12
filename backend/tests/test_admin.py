from bson import ObjectId
from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.main import app


def test_normal_user_is_forbidden_from_admin_api():
    app.dependency_overrides[get_current_user] = lambda: {"_id": ObjectId(), "role": "USER", "is_active": True}
    try:
        response = TestClient(app).get("/api/admin/dashboard")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)
