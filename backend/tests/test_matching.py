from datetime import date

from app.config import DETERMINISTIC_WEIGHT_TOTAL, MATCH_WEIGHTS
from app.schemas.eligibility import ConfidenceLevel, EligibilityDecision, EligibilityResult, EligibilitySummary
from app.schemas.matching import MatchDimensionStatus
from app.schemas.profile import ProfileCreate
from app.schemas.scheme import SchemeRecord
from app.services.matching import calculate_matching


def profile(**overrides):
    data = {
        "name": "Test Entrepreneur",
        "age": 24,
        "category": "OBC",
        "state": "Uttar Pradesh",
        "district": "Hathras",
        "business_type": "PROPRIETORSHIP",
        "business_sector": "FOOD_PROCESSING",
        "business_stage": "NEW",
        "annual_income": 250000,
        "investment_capacity": 300000,
        "loan_required": 500000,
    }
    data.update(overrides)
    return ProfileCreate.model_validate(data)


def scheme(**overrides):
    data = {
        "scheme_id": "DATA_DRIVEN_MATCH_SCHEME",
        "name": "Data-driven match scheme",
        "short_name": "MATCH",
        "description": "A structured test scheme.",
        "supported_categories": ["OBC"],
        "supported_locations": ["Uttar Pradesh"],
        "business_types": ["PROPRIETORSHIP"],
        "sectors": ["FOOD_PROCESSING"],
        "business_stages": ["NEW"],
        "income_rule": {"maximum": 300000},
        "investment_rule": {"maximum": 500000},
        "loan_rule": {"maximum": 600000},
        "official_source": "Official source",
        "official_source_url": "https://example.gov.in/match",
        "source_type": "OFFICIAL_GOVERNMENT",
        "last_verified": date.today(),
        "version": "1.0.0",
        "active": True,
    }
    data.update(overrides)
    return SchemeRecord.model_validate(data)


def eligibility(decision=EligibilityDecision.ELIGIBLE, confidence=ConfidenceLevel.HIGH):
    return EligibilityResult(
        scheme_id="DATA_DRIVEN_MATCH_SCHEME",
        decision=decision,
        confidence=confidence,
        rules=[],
        summary=EligibilitySummary(total_rules=0, passed=0, failed=0, unknown=0, not_applicable=0, invalid=0),
    )


def test_fully_matching_profile_scores_all_deterministic_dimensions():
    result = calculate_matching(profile(), scheme(), eligibility())
    assert result.eligible_for_matching is True
    assert result.deterministic_match_score == 100
    assert result.semantic_score is None
    assert result.final_match_score is None
    assert all(item.status == MatchDimensionStatus.MATCH for item in result.dimensions.values())


def test_category_mismatch_scores_zero():
    result = calculate_matching(profile(category="SC"), scheme(), eligibility())
    assert result.dimensions["category"].status == MatchDimensionStatus.NO_MATCH
    assert result.dimensions["category"].score == 0


def test_business_partial_match_is_not_ai_matching():
    result = calculate_matching(profile(business_sector="TEXTILE"), scheme(), eligibility())
    assert result.dimensions["business"].status == MatchDimensionStatus.PARTIAL_MATCH
    assert result.dimensions["business"].score == 50


def test_location_state_match_is_deterministic():
    result = calculate_matching(profile(state="Uttar Pradesh", district="Unknown District"), scheme(), eligibility())
    assert result.dimensions["location"].status == MatchDimensionStatus.MATCH


def test_location_mismatch_scores_zero():
    result = calculate_matching(profile(state="Kerala"), scheme(), eligibility())
    assert result.dimensions["location"].status == MatchDimensionStatus.NO_MATCH
    assert result.dimensions["location"].score == 0


def test_unknown_dimensions_are_excluded_from_denominator():
    result = calculate_matching(profile(category=None, business_sector=None, investment_capacity=None), scheme(), eligibility())
    assert result.deterministic_match_score == 100
    assert set(result.unknown_dimensions) == {"category", "business", "financial"}
    assert result.confidence == ConfidenceLevel.LOW


def test_not_applicable_dimensions_are_excluded():
    result = calculate_matching(profile(), scheme(supported_categories=[], supported_locations=[], business_types=[], sectors=[], business_stages=[], income_rule=None, investment_rule=None, loan_rule=None), eligibility())
    assert result.deterministic_match_score is None
    assert len(result.not_applicable_dimensions) == 5


def test_missing_business_stage_is_unknown():
    result = calculate_matching(profile(business_stage=None), scheme(), eligibility())
    assert result.dimensions["business_stage"].status == MatchDimensionStatus.UNKNOWN


def test_negative_financial_value_is_invalid():
    result = calculate_matching({**profile().model_dump(), "investment_capacity": -1}, scheme(), eligibility())
    assert result.dimensions["financial"].status == MatchDimensionStatus.INVALID


def test_not_eligible_is_gated_and_score_is_null():
    result = calculate_matching(profile(), scheme(), eligibility(EligibilityDecision.NOT_ELIGIBLE))
    assert result.eligible_for_matching is False
    assert result.deterministic_match_score is None
    assert result.explanations == ["Mandatory eligibility failed; a normal match score was not calculated."]


def test_needs_verification_can_still_be_scored():
    result = calculate_matching(profile(), scheme(), eligibility(EligibilityDecision.NEEDS_VERIFICATION, ConfidenceLevel.MEDIUM))
    assert result.eligible_for_matching is True
    assert result.deterministic_match_score == 100
    assert result.eligibility_status == EligibilityDecision.NEEDS_VERIFICATION


def test_no_scheme_financial_rule_is_not_applicable_not_zero():
    result = calculate_matching(profile(), scheme(income_rule=None, investment_rule=None, loan_rule=None), eligibility())
    assert result.dimensions["financial"].status == MatchDimensionStatus.NOT_APPLICABLE


def test_weights_are_85_deterministic_and_100_planned():
    assert DETERMINISTIC_WEIGHT_TOTAL == 85
    assert sum(MATCH_WEIGHTS.values()) == 100
    assert MATCH_WEIGHTS["semantic"] == 15


def test_matching_is_deterministic():
    first = calculate_matching(profile(), scheme(), eligibility()).model_dump()
    second = calculate_matching(profile(), scheme(), eligibility()).model_dump()
    assert first == second
