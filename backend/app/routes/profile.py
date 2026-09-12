from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Path, status
from fastapi import Depends
from pymongo.errors import PyMongoError

from app.database.mongodb import get_database
from app.core.security import get_current_user
from app.schemas.profile import ProfileCreate, ProfileResponse
from app.services.profiles import create_profile, get_owned_profile

router = APIRouter(prefix="/profile", tags=["profiles"])


def _profiles_collection():
    return get_database()["profiles"]


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an entrepreneur profile",
)
def create_profile_endpoint(profile: ProfileCreate, current_user: dict = Depends(get_current_user)) -> ProfileResponse:
    try:
        return create_profile(_profiles_collection(), profile, str(current_user["_id"]))
    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile storage is temporarily unavailable.",
        ) from error


@router.get(
    "/{profile_id}",
    response_model=ProfileResponse,
    summary="Retrieve an entrepreneur profile",
)
def get_profile_endpoint(
    profile_id: str = Path(min_length=1, description="MongoDB ObjectId of the profile"),
    current_user: dict = Depends(get_current_user),
) -> ProfileResponse:
    try:
        ObjectId(profile_id)
    except InvalidId as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid profile ID.",
        ) from error

    try:
        profile = get_owned_profile(_profiles_collection(), profile_id, str(current_user["_id"]))
    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile storage is temporarily unavailable.",
        ) from error

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    return profile
