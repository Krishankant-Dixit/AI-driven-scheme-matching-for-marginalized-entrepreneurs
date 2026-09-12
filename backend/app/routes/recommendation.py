from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pymongo.errors import PyMongoError

from app.config import DEFAULT_RECOMMENDATION_LIMIT, MAX_RECOMMENDATION_LIMIT
from app.core.security import get_current_user
from app.database.mongodb import get_database
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.profiles import get_owned_profile
from app.services.recommendation import generate_recommendations
from app.utils.scheme_data import load_rule_seed, load_runtime_scheme_seed

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse, summary="Generate ranked scheme recommendations")
def recommendations(
    request: RecommendationRequest = Body(...),
    limit: int = Query(DEFAULT_RECOMMENDATION_LIMIT, ge=1, le=MAX_RECOMMENDATION_LIMIT),
    current_user: dict = Depends(get_current_user),
) -> RecommendationResponse:
    profile_id = request.profile_id
    try:
        ObjectId(profile_id)
    except InvalidId as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid profile ID.") from error
    try:
        stored_profile = get_owned_profile(get_database()["profiles"], profile_id, str(current_user["_id"]))
    except PyMongoError as error:
        raise HTTPException(status_code=500, detail="Profile storage is temporarily unavailable.") from error
    if stored_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    try:
        schemes = load_runtime_scheme_seed(get_database()).schemes
        rules = load_rule_seed().rules
        result = generate_recommendations(stored_profile.profile, profile_id, schemes, rules, limit)
        history = result.model_dump(mode="json")
        history.update({"user_id": str(current_user["_id"]), "profile_id": profile_id, "scheme_versions": {item.scheme_id: item.version for item in result.recommendations + result.excluded}, "model_version": None})
        get_database()["recommendation_history"].create_index([("user_id", 1), ("generated_at", -1)])
        get_database()["recommendation_history"].insert_one(history)
        return result
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=500, detail="Recommendation data is temporarily unavailable.") from error
