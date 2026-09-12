from datetime import datetime, timezone

from bson import ObjectId
from pymongo.collection import Collection

from app.schemas.profile import ProfileCreate, ProfileResponse


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_profile(collection: Collection, profile: ProfileCreate, user_id: str) -> ProfileResponse:
    collection.create_index("user_id")
    timestamp = _utc_now()
    document = profile.model_dump(mode="json")
    document["created_at"] = timestamp
    document["updated_at"] = timestamp
    document["user_id"] = user_id
    result = collection.insert_one(document)
    return ProfileResponse(
        profile_id=str(result.inserted_id),
        profile=profile,
        created_at=timestamp,
        updated_at=timestamp,
    )


def get_profile(collection: Collection, profile_id: str) -> ProfileResponse | None:
    document = collection.find_one({"_id": ObjectId(profile_id)})
    if document is None:
        return None
    profile = ProfileCreate.model_validate(
        {key: value for key, value in document.items() if key not in {"_id", "created_at", "updated_at"}}
    )
    return ProfileResponse(
        profile_id=str(document["_id"]),
        profile=profile,
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


def get_owned_profile(collection: Collection, profile_id: str, user_id: str) -> ProfileResponse | None:
    document = collection.find_one({"_id": ObjectId(profile_id), "user_id": user_id})
    if document is None:
        return None
    profile = ProfileCreate.model_validate({key: value for key, value in document.items() if key not in {"_id", "user_id", "created_at", "updated_at"}})
    return ProfileResponse(profile_id=str(document["_id"]), profile=profile, created_at=document["created_at"], updated_at=document["updated_at"])
