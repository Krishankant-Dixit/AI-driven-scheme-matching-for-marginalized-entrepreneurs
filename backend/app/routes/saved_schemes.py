from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.core.security import get_current_user
from app.database.mongodb import get_database
from app.schemas.saved_scheme import SavedSchemeCreate, SavedSchemeResponse
from app.utils.scheme_data import load_runtime_scheme_seed

router = APIRouter(prefix="/saved-schemes", tags=["saved schemes"])


def _response(document: dict) -> SavedSchemeResponse:
    return SavedSchemeResponse(id=str(document["_id"]), scheme_id=document["scheme_id"], scheme_version=document["scheme_version"], saved_at=document["saved_at"])


@router.post("", response_model=SavedSchemeResponse, status_code=status.HTTP_201_CREATED)
def save_scheme(request: SavedSchemeCreate, current_user: dict = Depends(get_current_user)) -> SavedSchemeResponse:
    scheme = next((item for item in load_runtime_scheme_seed(get_database()).schemes if item.scheme_id == request.scheme_id and item.active), None)
    if scheme is None:
        raise HTTPException(status_code=404, detail="Active scheme not found.")
    collection = get_database()["saved_schemes"]
    collection.create_index([("user_id", 1), ("scheme_id", 1)], unique=True)
    document = {"user_id": str(current_user["_id"]), "scheme_id": scheme.scheme_id, "scheme_version": scheme.version, "saved_at": datetime.now(timezone.utc)}
    try:
        result = collection.insert_one(document)
    except DuplicateKeyError as error:
        raise HTTPException(status_code=409, detail="This scheme is already saved.") from error
    return _response({**document, "_id": result.inserted_id})


@router.get("", response_model=list[SavedSchemeResponse])
def list_saved_schemes(current_user: dict = Depends(get_current_user)) -> list[SavedSchemeResponse]:
    documents = get_database()["saved_schemes"].find({"user_id": str(current_user["_id"])}).sort("saved_at", -1)
    return [_response(document) for document in documents]


@router.delete("/{scheme_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_scheme(scheme_id: str, current_user: dict = Depends(get_current_user)) -> None:
    result = get_database()["saved_schemes"].delete_one({"user_id": str(current_user["_id"]), "scheme_id": scheme_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved scheme not found.")
