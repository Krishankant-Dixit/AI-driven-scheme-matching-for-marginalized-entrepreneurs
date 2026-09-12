from datetime import datetime, timezone
from typing import Any

from app.config import RECOMMENDATION_THRESHOLDS
from app.schemas.eligibility import EligibilityDecision
from app.schemas.matching import MatchDimensionStatus
from app.schemas.recommendation import (
    RecommendationCategory,
    RecommendationItem,
    RecommendationResponse,
    RecommendationSummary,
)
from app.schemas.scheme import SchemeRecord
from app.services.eligibility import evaluate_eligibility
from app.services.matching import calculate_matching
from app.services.ranking import rank_recommendations


def _category(decision: EligibilityDecision, score: float | None) -> RecommendationCategory:
    if decision == EligibilityDecision.NOT_ELIGIBLE or decision == EligibilityDecision.INVALID:
        return RecommendationCategory.NOT_RECOMMENDED
    if decision == EligibilityDecision.NEEDS_VERIFICATION:
        return RecommendationCategory.NEEDS_VERIFICATION
    if score is None or score < RECOMMENDATION_THRESHOLDS["potentially_relevant"]:
        return RecommendationCategory.NOT_RECOMMENDED
    if score >= RECOMMENDATION_THRESHOLDS["highly_recommended"]:
        return RecommendationCategory.HIGHLY_RECOMMENDED
    if score >= RECOMMENDATION_THRESHOLDS["recommended"]:
        return RecommendationCategory.RECOMMENDED
    return RecommendationCategory.POTENTIALLY_RELEVANT


def _item(profile: Any, profile_id: str, scheme: SchemeRecord, rules: list[Any]) -> RecommendationItem:
    eligibility = evaluate_eligibility(profile, scheme.scheme_id, rules, scheme)
    matching = calculate_matching(profile, scheme, eligibility, profile_id)
    score = matching.deterministic_match_score
    category = _category(eligibility.decision, score)
    missing = [name for name in matching.unknown_dimensions]
    explanations = []
    if eligibility.decision == EligibilityDecision.NOT_ELIGIBLE:
        explanations.append("This scheme was not recommended because a mandatory eligibility condition was not satisfied.")
    elif eligibility.decision == EligibilityDecision.NEEDS_VERIFICATION:
        explanations.append("Eligibility could not be confirmed because some mandatory information is missing.")
    explanations.extend(matching.explanations)
    explanations.extend(eligibility.verification_warnings)
    breakdown = {name: dimension.score for name, dimension in matching.dimensions.items()}
    return RecommendationItem(
        scheme_id=scheme.scheme_id,
        scheme_name=scheme.name,
        eligibility_status=eligibility.decision,
        recommendation_category=category,
        final_match_score=None,
        deterministic_match_score=score,
        semantic_score=None,
        confidence=matching.confidence,
        score_breakdown=breakdown,
        explanations=list(dict.fromkeys(explanations)),
        verification_required=eligibility.decision == EligibilityDecision.NEEDS_VERIFICATION or bool(eligibility.verification_warnings),
        missing_information=missing,
        official_source=scheme.official_source,
        official_source_url=scheme.official_source_url,
        source_type=scheme.source_type.value,
        last_verified=scheme.last_verified.isoformat(),
        version=scheme.version,
        ranking_score=score,
    )


def generate_recommendations(profile: Any, profile_id: str, schemes: list[SchemeRecord], rules: list[Any], limit: int) -> RecommendationResponse:
    active_schemes = [scheme for scheme in schemes if scheme.active]
    items = [_item(profile, profile_id, scheme, [rule for rule in rules if rule.scheme_id == scheme.scheme_id]) for scheme in active_schemes]
    ranked = rank_recommendations(items)
    primary = [item for item in ranked if item.recommendation_category != RecommendationCategory.NOT_RECOMMENDED]
    excluded = [item for item in ranked if item.recommendation_category == RecommendationCategory.NOT_RECOMMENDED]
    selected = primary[:limit]
    for rank, item in enumerate(selected, start=1):
        item.rank = rank
    summary = RecommendationSummary(
        evaluated=len(active_schemes),
        eligible=sum(item.eligibility_status == EligibilityDecision.ELIGIBLE for item in items),
        needs_verification=sum(item.eligibility_status == EligibilityDecision.NEEDS_VERIFICATION for item in items),
        not_eligible=sum(item.eligibility_status in {EligibilityDecision.NOT_ELIGIBLE, EligibilityDecision.INVALID} for item in items),
        recommended=len(selected),
    )
    return RecommendationResponse(
        profile_id=profile_id,
        generated_at=datetime.now(timezone.utc),
        total_schemes_evaluated=len(active_schemes),
        total_recommendations=len(selected),
        summary=summary,
        recommendations=selected,
        excluded=excluded,
    )
