from datetime import date

from app.schemas.recommendation import RecommendationItem

_CONFIDENCE_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
_STATUS_ORDER = {"ELIGIBLE": 0, "NEEDS_VERIFICATION": 1, "NOT_ELIGIBLE": 2, "INVALID": 3}


def rank_recommendations(items: list[RecommendationItem]) -> list[RecommendationItem]:
    return sorted(
        items,
        key=lambda item: (
            _STATUS_ORDER.get(item.eligibility_status.value, 99),
            -(item.ranking_score if item.ranking_score is not None else -1),
            _CONFIDENCE_ORDER.get(item.confidence.value, 99),
            -date.fromisoformat(item.last_verified).toordinal(),
            item.scheme_id,
        ),
    )
