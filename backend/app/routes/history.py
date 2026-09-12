from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user
from app.database.mongodb import get_database

router = APIRouter(prefix="/recommendations/history", tags=["recommendation history"])


def _owned_id(value: str):
    try:
        return ObjectId(value)
    except InvalidId as error:
        raise HTTPException(status_code=400, detail="Invalid history ID.") from error


@router.get("")
def list_history(limit: int = Query(10, ge=1, le=50), page: int = Query(1, ge=1), current_user: dict = Depends(get_current_user)) -> list[dict]:
    cursor = get_database()["recommendation_history"].find({"user_id": str(current_user["_id"])}).sort("generated_at", -1).skip((page - 1) * limit).limit(limit)
    return [{**item, "_id": str(item["_id"])} for item in cursor]


@router.get("/{history_id}")
def history_detail(history_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    document = get_database()["recommendation_history"].find_one({"_id": _owned_id(history_id), "user_id": str(current_user["_id"])})
    if document is None:
        raise HTTPException(status_code=404, detail="Recommendation history not found.")
    document["_id"] = str(document["_id"])
    return document


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(history_id: str, current_user: dict = Depends(get_current_user)) -> None:
    result = get_database()["recommendation_history"].delete_one({"_id": _owned_id(history_id), "user_id": str(current_user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Recommendation history not found.")