import math
from typing import Any

from app.config import MATCH_WEIGHTS
from app.schemas.common import ValueState
from app.schemas.eligibility import ConfidenceLevel, EligibilityDecision, EligibilityResult
from app.schemas.matching import MatchDimension, MatchDimensionStatus, MatchingResult
from app.schemas.profile import ProfileCreate
from app.schemas.scheme import SchemeRecord

_MISSING = object()


def _values(profile: ProfileCreate | dict[str, Any]) -> dict[str, Any]:
    return profile.model_dump(mode="json") if isinstance(profile, ProfileCreate) else profile


def _enum(value: Any) -> Any:
    return getattr(value, "value", value)


def _missing(value: Any) -> bool:
    return value is _MISSING or value is None or value == "" or value == "UNKNOWN"


def _dimension(name: str, status: MatchDimensionStatus, weight: int, user: Any, scheme: Any, message: str, score: float | None = None) -> MatchDimension:
    return MatchDimension(dimension=name, score=score, weight=weight, status=status, user_value=None if user is _MISSING else user, scheme_value=scheme, message=message)


def _list_value(scheme: SchemeRecord | dict[str, Any], field: str) -> list[Any]:
    value = getattr(scheme, field, None) if isinstance(scheme, SchemeRecord) else scheme.get(field)
    return value or []


def _category(values: dict[str, Any], scheme: SchemeRecord | dict[str, Any]) -> MatchDimension:
    supported = _list_value(scheme, "supported_categories")
    user = values.get("category", _MISSING)
    if not supported:
        return _dimension("CATEGORY", MatchDimensionStatus.NOT_APPLICABLE, MATCH_WEIGHTS["category"], user, supported, "The scheme does not define supported categories.")
    if _missing(user):
        return _dimension("CATEGORY", MatchDimensionStatus.UNKNOWN, MATCH_WEIGHTS["category"], user, supported, "Category matching cannot be evaluated because category information is missing.")
    if user in supported:
        return _dimension("CATEGORY", MatchDimensionStatus.MATCH, MATCH_WEIGHTS["category"], user, supported, "Category matches the scheme's supported categories.", 100)
    return _dimension("CATEGORY", MatchDimensionStatus.NO_MATCH, MATCH_WEIGHTS["category"], user, supported, "Category is not listed as supported by the scheme.", 0)


def _business(values: dict[str, Any], scheme: SchemeRecord | dict[str, Any]) -> MatchDimension:
    supported_types = _list_value(scheme, "business_types")
    supported_sectors = _list_value(scheme, "sectors")
    criteria = [("business_type", supported_types), ("business_sector", supported_sectors)]
    applicable = [(field, allowed) for field, allowed in criteria if allowed]
    if not applicable:
        return _dimension("BUSINESS", MatchDimensionStatus.NOT_APPLICABLE, MATCH_WEIGHTS["business"], None, [], "The scheme does not define structured business criteria.")
    component_scores = []
    unknown = False
    for field, allowed in applicable:
        value = values.get(field, _MISSING)
        if _missing(value):
            unknown = True
        else:
            component_scores.append(100 if value in allowed else 0)
    if not component_scores:
        return _dimension("BUSINESS", MatchDimensionStatus.UNKNOWN, MATCH_WEIGHTS["business"], None, applicable, "Business matching cannot be evaluated because structured business information is missing.")
    score = sum(component_scores) / len(component_scores)
    if unknown:
        return _dimension("BUSINESS", MatchDimensionStatus.UNKNOWN, MATCH_WEIGHTS["business"], None, applicable, "Business matching is partial because some structured business information is missing.", score)
    if score == 100:
        status = MatchDimensionStatus.MATCH
        message = "Business type and sector match the structured scheme criteria."
    elif score == 0:
        status = MatchDimensionStatus.NO_MATCH
        message = "Business type and sector do not match the structured scheme criteria."
    else:
        status = MatchDimensionStatus.PARTIAL_MATCH
        message = "Some structured business criteria match the scheme."
    return _dimension("BUSINESS", status, MATCH_WEIGHTS["business"], values, applicable, message, score)


def _location(values: dict[str, Any], scheme: SchemeRecord | dict[str, Any]) -> MatchDimension:
    supported = _list_value(scheme, "supported_locations")
    user_state = values.get("state", _MISSING)
    user_district = values.get("district", _MISSING)
    if not supported:
        return _dimension("LOCATION", MatchDimensionStatus.NOT_APPLICABLE, MATCH_WEIGHTS["location"], {"state": user_state, "district": user_district}, supported, "The scheme does not define structured location criteria.")
    if _missing(user_state) or _missing(user_district):
        return _dimension("LOCATION", MatchDimensionStatus.UNKNOWN, MATCH_WEIGHTS["location"], {"state": user_state, "district": user_district}, supported, "Location matching cannot be evaluated because state or district information is missing.")
    normalized = {str(item).upper() for item in supported}
    if "INDIA" in normalized or str(user_state).upper() in normalized or str(user_district).upper() in normalized:
        return _dimension("LOCATION", MatchDimensionStatus.MATCH, MATCH_WEIGHTS["location"], {"state": user_state, "district": user_district}, supported, "State or district is supported by the scheme.", 100)
    return _dimension("LOCATION", MatchDimensionStatus.NO_MATCH, MATCH_WEIGHTS["location"], {"state": user_state, "district": user_district}, supported, "Location is not listed as supported by the scheme.", 0)


def _financial(values: dict[str, Any], scheme: SchemeRecord | dict[str, Any]) -> MatchDimension:
    rules = []
    for field, scheme_field in (("annual_income", "income_rule"), ("investment_capacity", "investment_rule"), ("loan_required", "loan_rule")):
        config = getattr(scheme, scheme_field, None) if isinstance(scheme, SchemeRecord) else scheme.get(scheme_field)
        if isinstance(config, dict) and config.get("state") != "UNKNOWN" and config:
            rules.append((field, config))
    if not rules:
        return _dimension("FINANCIAL", MatchDimensionStatus.NOT_APPLICABLE, MATCH_WEIGHTS["financial"], None, None, "The scheme does not define applicable financial criteria.")
    scores = []
    for field, config in rules:
        value = values.get(field, _MISSING)
        if _missing(value):
            return _dimension("FINANCIAL", MatchDimensionStatus.UNKNOWN, MATCH_WEIGHTS["financial"], value, config, "Financial compatibility could not be evaluated because financial information is missing.")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            return _dimension("FINANCIAL", MatchDimensionStatus.INVALID, MATCH_WEIGHTS["financial"], value, config, "Financial information is invalid and must be corrected.")
        minimum = config.get("minimum", config.get("min"))
        maximum = config.get("maximum", config.get("max"))
        if minimum is not None and value < minimum:
            scores.append(0)
        elif maximum is not None and value > maximum:
            scores.append(0)
        else:
            scores.append(100)
    score = sum(scores) / len(scores)
    status = MatchDimensionStatus.MATCH if score == 100 else MatchDimensionStatus.NO_MATCH if score == 0 else MatchDimensionStatus.PARTIAL_MATCH
    return _dimension("FINANCIAL", status, MATCH_WEIGHTS["financial"], {field: values.get(field) for field, _ in rules}, rules, "Financial information is compatible with the structured scheme criteria." if score == 100 else "Financial information is outside the structured scheme criteria.", score)


def _business_stage(values: dict[str, Any], scheme: SchemeRecord | dict[str, Any]) -> MatchDimension:
    supported = _list_value(scheme, "business_stages")
    user = values.get("business_stage", _MISSING)
    if not supported:
        return _dimension("BUSINESS_STAGE", MatchDimensionStatus.NOT_APPLICABLE, MATCH_WEIGHTS["business_stage"], user, supported, "The scheme does not define structured business-stage criteria.")
    if _missing(user):
        return _dimension("BUSINESS_STAGE", MatchDimensionStatus.UNKNOWN, MATCH_WEIGHTS["business_stage"], user, supported, "Business-stage matching cannot be evaluated because business stage is missing.")
    if user in supported:
        return _dimension("BUSINESS_STAGE", MatchDimensionStatus.MATCH, MATCH_WEIGHTS["business_stage"], user, supported, "Business stage matches the scheme's supported stages.", 100)
    return _dimension("BUSINESS_STAGE", MatchDimensionStatus.NO_MATCH, MATCH_WEIGHTS["business_stage"], user, supported, "Business stage does not match the scheme's supported stages.", 0)


def calculate_matching(profile: ProfileCreate | dict[str, Any], scheme: SchemeRecord | dict[str, Any], eligibility: EligibilityResult, profile_id: str | None = None) -> MatchingResult:
    dimensions = {
        "category": _category(_values(profile), scheme),
        "business": _business(_values(profile), scheme),
        "location": _location(_values(profile), scheme),
        "financial": _financial(_values(profile), scheme),
        "business_stage": _business_stage(_values(profile), scheme),
    }
    if eligibility.decision == EligibilityDecision.NOT_ELIGIBLE:
        return MatchingResult(profile_id=profile_id, scheme_id=eligibility.scheme_id, eligibility_status=eligibility.decision, eligible_for_matching=False, dimensions=dimensions, unknown_dimensions=[], not_applicable_dimensions=[], confidence=eligibility.confidence, explanations=["Mandatory eligibility failed; a normal match score was not calculated."])
    unknown = [name for name, item in dimensions.items() if item.status in {MatchDimensionStatus.UNKNOWN, MatchDimensionStatus.INVALID}]
    not_applicable = [name for name, item in dimensions.items() if item.status == MatchDimensionStatus.NOT_APPLICABLE]
    applicable = [
        item for item in dimensions.values()
        if item.score is not None
        and item.status in {
            MatchDimensionStatus.MATCH,
            MatchDimensionStatus.PARTIAL_MATCH,
            MatchDimensionStatus.NO_MATCH,
        }
    ]
    score = None if not applicable else sum(item.score * item.weight for item in applicable) / sum(item.weight for item in applicable)
    explanations = [item.message for item in dimensions.values()]
    if score is None:
        explanations.append("There is insufficient structured information to calculate a meaningful deterministic match score.")
    confidence = eligibility.confidence
    if len(unknown) >= 2 or any(item.status == MatchDimensionStatus.INVALID for item in dimensions.values()):
        confidence = ConfidenceLevel.LOW
    elif unknown or eligibility.decision == EligibilityDecision.NEEDS_VERIFICATION:
        confidence = ConfidenceLevel.MEDIUM if confidence == ConfidenceLevel.HIGH else confidence
    return MatchingResult(profile_id=profile_id, scheme_id=eligibility.scheme_id, eligibility_status=eligibility.decision, eligible_for_matching=True, deterministic_match_score=score, dimensions=dimensions, unknown_dimensions=unknown, not_applicable_dimensions=not_applicable, confidence=confidence, explanations=explanations)
