from datetime import date, timedelta

from app.schemas.eligibility import ConfidenceLevel, EligibilityDecision
from app.schemas.recommendation import RecommendationCategory
from app.schemas.profile import ProfileCreate
from app.schemas.scheme import SchemeRecord
from app.services.recommendation import generate_recommendations


def profile():
    return ProfileCreate(
        name="Test Entrepreneur", state="Uttar Pradesh", district="Hathras",
        category="OBC", business_type="PROPRIETORSHIP", business_sector="FOOD_PROCESSING",
        business_stage="NEW", annual_income=100000, investment_capacity=100000, loan_required=100000,
    )


def scheme(scheme_id, active=True, verified=date.today(), locations=None):
    return SchemeRecord(
        scheme_id=scheme_id, name=scheme_id, short_name=scheme_id, description="Test scheme",
        supported_categories=["OBC"], supported_locations=locations or ["Uttar Pradesh"],
        business_types=["PROPRIETORSHIP"], sectors=["FOOD_PROCESSING"], business_stages=["NEW"],
        official_source="Official source", official_source_url="https://example.gov.in/scheme",
        source_type="OFFICIAL_GOVERNMENT", last_verified=verified, version="1.0.0", active=active,
    )


def test_active_schemes_only_and_stable_recommendations():
    result = generate_recommendations(profile(), "profile-1", [scheme("B"), scheme("A"), scheme("OFF", False)], [], 10)
    assert result.total_schemes_evaluated == 2
    assert [item.scheme_id for item in result.recommendations] == ["A", "B"]


def test_inactive_scheme_is_excluded():
    result = generate_recommendations(profile(), "profile-1", [scheme("OFF", False)], [], 10)
    assert result.recommendations == []
    assert result.total_schemes_evaluated == 0


def test_needs_verification_is_labeled_and_can_appear():
    rules = [{
        "rule_id": "required-age", "scheme_id": "VERIFY", "rule_type": "AGE", "field": "age",
        "operator": "GREATER_THAN_OR_EQUAL", "expected_value": 18, "mandatory": True,
        "source": "https://example.gov.in/rule", "verification_status": "VERIFIED", "source_type": "OFFICIAL_GOVERNMENT",
    }]
    from app.schemas.rule import SchemeRule
    result = generate_recommendations(profile(), "profile-1", [scheme("VERIFY")], [SchemeRule.model_validate(rules[0])], 10)
    assert result.recommendations[0].recommendation_category == RecommendationCategory.NEEDS_VERIFICATION
    assert result.recommendations[0].verification_required is True


def test_not_eligible_is_excluded_from_primary_results():
    from app.schemas.rule import SchemeRule
    rule = SchemeRule(
        rule_id="category", scheme_id="FAIL", rule_type="CATEGORY", field="category", operator="EQUALS",
        expected_value="SC", mandatory=True, source="https://example.gov.in/rule",
        verification_status="VERIFIED", source_type="OFFICIAL_GOVERNMENT",
    )
    result = generate_recommendations(profile(), "profile-1", [scheme("FAIL")], [rule], 10)
    assert result.recommendations == []
    assert result.excluded[0].recommendation_category == RecommendationCategory.NOT_RECOMMENDED


def test_limit_is_applied_after_stable_ranking():
    result = generate_recommendations(profile(), "profile-1", [scheme("C"), scheme("B"), scheme("A")], [], 2)
    assert [item.scheme_id for item in result.recommendations] == ["A", "B"]
    assert [item.rank for item in result.recommendations] == [1, 2]


def test_semantic_and_final_scores_remain_null_without_phase_seven():
    result = generate_recommendations(profile(), "profile-1", [scheme("A")], [], 10)
    assert result.recommendations[0].semantic_score is None
    assert result.recommendations[0].final_match_score is None