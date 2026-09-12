from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import PyMongoError

from app.database.mongodb import get_database
from app.core.security import get_current_user
from app.schemas.eligibility import EligibilityCheckRequest
from app.schemas.matching import MatchingResult
from app.services.eligibility import evaluate_eligibility
from app.services.matching import calculate_matching
from app.services.profiles import get_owned_profile
from app.utils.scheme_data import load_rule_seed, load_runtime_scheme_seed

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post(
    "/score",
    response_model=MatchingResult,
    summary="Calculate a deterministic match score",
    description="Runs hard eligibility first, then scores structured deterministic dimensions. Semantic and final scores remain null in Phase 6.",
)
def score_matching(request: EligibilityCheckRequest, current_user: dict = Depends(get_current_user)) -> MatchingResult:
    try:
        ObjectId(request.profile_id)
    except InvalidId as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid profile ID.") from error
    try:
        stored_profile = get_owned_profile(get_database()["profiles"], request.profile_id, str(current_user["_id"]))
    except PyMongoError as error:
        raise HTTPException(status_code=500, detail="Profile storage is temporarily unavailable.") from error
    if stored_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    try:
        schemes = load_runtime_scheme_seed(get_database()).schemes
        rules = load_rule_seed().rules
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=500, detail="Scheme data is temporarily unavailable.") from error
    scheme = next((item for item in schemes if item.scheme_id == request.scheme_id), None)
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    eligibility = evaluate_eligibility(
        stored_profile.profile,
        request.scheme_id,
        [rule for rule in rules if rule.scheme_id == request.scheme_id],
        scheme,
    )
    return calculate_matching(stored_profile.profile, scheme, eligibility, request.profile_id)