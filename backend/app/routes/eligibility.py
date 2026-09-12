from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import PyMongoError

from app.database.mongodb import get_database
from app.core.security import get_current_user
from app.schemas.eligibility import EligibilityCheckRequest, EligibilityResult
from app.services.eligibility import evaluate_eligibility
from app.services.profiles import get_owned_profile
from app.utils.scheme_data import load_rule_seed, load_runtime_scheme_seed

router = APIRouter(prefix="/eligibility", tags=["eligibility"])


@router.post(
    "/check",
    response_model=EligibilityResult,
    summary="Evaluate mandatory scheme rules for a profile",
    description="Evaluates structured mandatory rules only. It does not use AI, scoring, ranking, or scheme-specific code.",
)
def check_eligibility(request: EligibilityCheckRequest, current_user: dict = Depends(get_current_user)) -> EligibilityResult:
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
        raise HTTPException(status_code=500, detail="Scheme rule data is temporarily unavailable.") from error

    scheme = next((scheme for scheme in schemes if scheme.scheme_id == request.scheme_id), None)
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    scheme_rules = [rule for rule in rules if rule.scheme_id == request.scheme_id]
    return evaluate_eligibility(stored_profile.profile, request.scheme_id, scheme_rules, scheme)
