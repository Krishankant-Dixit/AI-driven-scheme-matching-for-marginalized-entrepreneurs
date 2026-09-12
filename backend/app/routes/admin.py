from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError, PyMongoError
from pydantic import BaseModel

from app.core.admin import require_admin
from app.database.mongodb import get_database
from app.schemas.scheme import SchemeRecord
from app.utils.scheme_data import load_rule_seed, load_runtime_scheme_seed

router = APIRouter(prefix="/admin", tags=["admin"])


class StatusUpdate(BaseModel):
    active: bool


def _audit(user: dict, action: str, resource_type: str, resource_id: str, details: dict | None = None) -> None:
    get_database()["audit_logs"].create_index([("timestamp", -1)])
    get_database()["audit_logs"].insert_one({"user_id": str(user["_id"]), "action": action, "resource_type": resource_type, "resource_id": resource_id, "timestamp": datetime.now(timezone.utc), "details": details or {}})


@router.get("/dashboard")
def dashboard(_: dict = Depends(require_admin)) -> dict:
    database = get_database()
    schemes = list(load_runtime_scheme_seed(database).schemes)
    users = database["users"].count_documents({})
    history = database["recommendation_history"].count_documents({})
    warnings = [scheme.scheme_id for scheme in schemes if not scheme.active or not scheme.last_verified or not scheme.official_source_url]
    return {"schemes": {"total": len(schemes), "active": sum(item.active for item in schemes), "inactive": sum(not item.active for item in schemes)}, "users": users, "recommendation_activity": history, "data_quality_warnings": warnings}


@router.get("/schemes", response_model=list[SchemeRecord])
def list_schemes(_: dict = Depends(require_admin)) -> list[SchemeRecord]:
    return load_runtime_scheme_seed(get_database()).schemes


@router.get("/schemes/{scheme_id}", response_model=SchemeRecord)
def get_scheme(scheme_id: str, _: dict = Depends(require_admin)) -> SchemeRecord:
    scheme = next((item for item in load_runtime_scheme_seed(get_database()).schemes if item.scheme_id == scheme_id), None)
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    return scheme


@router.post("/schemes", response_model=SchemeRecord, status_code=status.HTTP_201_CREATED)
def create_scheme(scheme: SchemeRecord, user: dict = Depends(require_admin)) -> SchemeRecord:
    if not scheme.official_source_url or not scheme.version:
        raise HTTPException(status_code=422, detail="Official source, verification date, and version are required.")
    collection = get_database()["schemes"]
    collection.create_index("scheme_id", unique=True)
    try:
        collection.insert_one(scheme.model_dump(mode="json"))
    except DuplicateKeyError as error:
        raise HTTPException(status_code=409, detail="A scheme with this ID already exists.") from error
    _audit(user, "SCHEME_CREATED", "SCHEME", scheme.scheme_id)
    return scheme


@router.put("/schemes/{scheme_id}", response_model=SchemeRecord)
def update_scheme(scheme_id: str, scheme: SchemeRecord, user: dict = Depends(require_admin)) -> SchemeRecord:
    if scheme.scheme_id != scheme_id:
        raise HTTPException(status_code=400, detail="Scheme ID cannot be changed.")
    result = get_database()["schemes"].replace_one({"scheme_id": scheme_id}, scheme.model_dump(mode="json"), upsert=True)
    _audit(user, "SCHEME_UPDATED", "SCHEME", scheme_id)
    return scheme


@router.patch("/schemes/{scheme_id}/status", response_model=dict)
def update_scheme_status(scheme_id: str, request: StatusUpdate, user: dict = Depends(require_admin)) -> dict:
    managed = next((item for item in load_runtime_scheme_seed(get_database()).schemes if item.scheme_id == scheme_id), None)
    if managed is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    get_database()["schemes"].replace_one({"scheme_id": scheme_id}, {**managed.model_dump(mode="json"), "active": request.active}, upsert=True)
    _audit(user, "SCHEME_ACTIVATED" if request.active else "SCHEME_DEACTIVATED", "SCHEME", scheme_id)
    return {"scheme_id": scheme_id, "active": request.active}


@router.delete("/schemes/{scheme_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheme(scheme_id: str, user: dict = Depends(require_admin)) -> None:
    result = get_database()["schemes"].delete_one({"scheme_id": scheme_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Scheme not found in managed records.")
    _audit(user, "SCHEME_DELETED", "SCHEME", scheme_id)


@router.get("/users")
def list_users(_: dict = Depends(require_admin)) -> list[dict]:
    return [{"id": str(user["_id"]), "name": user["name"], "email": user["email"], "role": user.get("role", "USER"), "is_active": user.get("is_active", False), "created_at": user["created_at"]} for user in get_database()["users"].find({}, {"password_hash": 0})]


@router.patch("/users/{user_id}/status")
def update_user_status(user_id: str, request: StatusUpdate, admin: dict = Depends(require_admin)) -> dict:
    try:
        object_id = ObjectId(user_id)
    except InvalidId as error:
        raise HTTPException(status_code=400, detail="Invalid user ID.") from error
    result = get_database()["users"].update_one({"_id": object_id}, {"$set": {"is_active": request.active}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    _audit(admin, "USER_STATUS_UPDATED", "USER", user_id, {"active": request.active})
    return {"id": user_id, "is_active": request.active}


@router.get("/data-quality")
def data_quality(_: dict = Depends(require_admin)) -> dict:
    schemes = load_runtime_scheme_seed(get_database()).schemes
    rules = load_rule_seed().rules
    errors = [scheme.scheme_id for scheme in schemes if not scheme.official_source_url or not scheme.version]
    warnings = [scheme.scheme_id for scheme in schemes if not scheme.active or scheme.source_type.value not in {"OFFICIAL_GOVERNMENT", "OFFICIAL_PORTAL"}]
    return {"status": "ERROR" if errors else "WARNING" if warnings else "GOOD", "errors": errors, "warnings": warnings, "rule_count": len(rules)}
