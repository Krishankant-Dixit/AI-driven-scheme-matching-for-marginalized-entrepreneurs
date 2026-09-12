from datetime import date, timedelta

import pytest

from app.schemas.common import ValueState
from app.schemas.eligibility import ConfidenceLevel, EligibilityDecision
from app.schemas.profile import ProfileCreate
from app.schemas.rule import RuleOperator, RuleType, SchemeRule
from app.services.eligibility import evaluate_eligibility, evaluate_rule
from app.schemas.scheme import SchemeRecord


def profile(**overrides):
    data = {
        "name": "Test Entrepreneur",
        "age": 24,
        "gender": "FEMALE",
        "category": "OBC",
        "state": "Uttar Pradesh",
        "district": "Hathras",
        "rural_urban": "RURAL",
        "business_type": "PROPRIETORSHIP",
        "business_sector": "FOOD_PROCESSING",
        "business_stage": "NEW",
        "annual_income": 250000,
        "investment_capacity": 300000,
        "loan_required": 500000,
    }
    data.update(overrides)
    return ProfileCreate.model_validate(data)


def rule(rule_type, field, operator, expected, mandatory=True, rule_id="test-rule"):
    return SchemeRule(
        rule_id=rule_id,
        scheme_id="DATA_DRIVEN_TEST_SCHEME",
        rule_type=rule_type,
        field=field,
        operator=operator,
        expected_value=expected,
        mandatory=mandatory,
        source="https://example.gov.in/rules",
        verification_status="VERIFIED",
        source_type="OFFICIAL_GOVERNMENT",
    )


def scheme(last_verified=None, source_type="OFFICIAL_GOVERNMENT", active=True):
    return SchemeRecord(
        scheme_id="DATA_DRIVEN_TEST_SCHEME",
        name="Data-driven test scheme",
        short_name="TEST",
        description="A test scheme.",
        official_source="Official source",
        official_source_url="https://example.gov.in/test",
        source_type=source_type,
        last_verified=last_verified or date.today(),
        version="1.0.0",
        active=active,
    )


@pytest.mark.parametrize(
    ("rule_type", "field", "operator", "expected", "overrides"),
    [
        (RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, {}),
        (RuleType.CATEGORY, "category", RuleOperator.IN, ["SC", "OBC"], {}),
        (RuleType.GENDER, "gender", RuleOperator.EQUALS, "FEMALE", {}),
        (RuleType.RURAL_URBAN, "rural_urban", RuleOperator.EQUALS, "RURAL", {}),
        (RuleType.BUSINESS_SECTOR, "business_sector", RuleOperator.EQUALS, "FOOD_PROCESSING", {}),
        (RuleType.BUSINESS_STAGE, "business_stage", RuleOperator.EQUALS, "NEW", {}),
        (RuleType.NEW_ENTERPRISE, "business_stage", RuleOperator.EQUALS, "NEW", {}),
        (RuleType.INCOME, "annual_income", RuleOperator.LESS_THAN_OR_EQUAL, 300000, {}),
        (RuleType.INVESTMENT, "investment_capacity", RuleOperator.LESS_THAN_OR_EQUAL, 400000, {}),
        (RuleType.LOAN_REQUIREMENT, "loan_required", RuleOperator.LESS_THAN_OR_EQUAL, 600000, {}),
    ],
)
def test_rule_passes(rule_type, field, operator, expected, overrides):
    result = evaluate_rule(profile(**overrides), rule(rule_type, field, operator, expected))
    assert result.status == ValueState.PASS


@pytest.mark.parametrize(
    ("rule_type", "field", "operator", "expected", "overrides"),
    [
        (RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 30, {}),
        (RuleType.CATEGORY, "category", RuleOperator.IN, ["SC", "ST"], {}),
        (RuleType.GENDER, "gender", RuleOperator.EQUALS, "MALE", {}),
        (RuleType.RURAL_URBAN, "rural_urban", RuleOperator.EQUALS, "URBAN", {}),
        (RuleType.BUSINESS_SECTOR, "business_sector", RuleOperator.EQUALS, "TEXTILE", {}),
        (RuleType.NEW_ENTERPRISE, "business_stage", RuleOperator.EQUALS, "NEW", {"business_stage": "EXISTING"}),
        (RuleType.INCOME, "annual_income", RuleOperator.LESS_THAN_OR_EQUAL, 100000, {}),
        (RuleType.INVESTMENT, "investment_capacity", RuleOperator.LESS_THAN_OR_EQUAL, 100000, {}),
        (RuleType.LOAN_REQUIREMENT, "loan_required", RuleOperator.LESS_THAN_OR_EQUAL, 100000, {}),
    ],
)
def test_rule_fails(rule_type, field, operator, expected, overrides):
    result = evaluate_rule(profile(**overrides), rule(rule_type, field, operator, expected))
    assert result.status == ValueState.FAIL


@pytest.mark.parametrize("field", ["age", "category", "gender", "rural_urban", "business_sector", "business_stage", "annual_income", "investment_capacity", "loan_required"])
def test_missing_rule_value_is_unknown(field):
    result = evaluate_rule(profile(**{field: None}), rule(RuleType.BUSINESS_STAGE if field == "business_stage" else RuleType.REQUIRED_INFORMATION, field, RuleOperator.REQUIRED, True))
    assert result.status == ValueState.UNKNOWN


def test_negative_financial_value_is_invalid():
    result = evaluate_rule({"annual_income": -1}, rule(RuleType.INCOME, "annual_income", RuleOperator.LESS_THAN_OR_EQUAL, 100))
    assert result.status == ValueState.INVALID


def test_existing_business_fails_new_enterprise_rule():
    result = evaluate_rule(profile(business_stage="EXISTING"), rule(RuleType.NEW_ENTERPRISE, "business_stage", RuleOperator.EQUALS, "NEW"))
    assert result.status == ValueState.FAIL


def test_required_information_passes_when_present():
    result = evaluate_rule(profile(annual_income=100), rule(RuleType.REQUIRED_INFORMATION, "annual_income", RuleOperator.REQUIRED, True))
    assert result.status == ValueState.PASS


def test_multiple_pass_rules_are_eligible():
    result = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, rule_id="age"),
        rule(RuleType.GENDER, "gender", RuleOperator.EQUALS, "FEMALE", rule_id="gender"),
    ])
    assert result.decision == EligibilityDecision.ELIGIBLE


def test_unknown_without_fail_needs_verification():
    result = evaluate_eligibility(profile(age=None), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18),
    ])
    assert result.decision == EligibilityDecision.NEEDS_VERIFICATION


def test_fail_takes_precedence_over_unknown():
    result = evaluate_eligibility(profile(age=16), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, rule_id="age"),
        rule(RuleType.GENDER, "gender", RuleOperator.EQUALS, "MALE", rule_id="gender"),
    ])
    assert result.decision == EligibilityDecision.NOT_ELIGIBLE


def test_not_applicable_plus_pass_is_eligible():
    result = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.CUSTOM, "future_condition", RuleOperator.CUSTOM, None, rule_id="future"),
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, rule_id="age"),
    ])
    assert result.decision == EligibilityDecision.ELIGIBLE


def test_invalid_rule_configuration_is_explicit():
    result = evaluate_rule(profile(), rule(RuleType.AGE, "age", RuleOperator.BETWEEN, [18], rule_id="invalid"))
    assert result.status == ValueState.INVALID


def test_invalid_expected_value_is_explicit():
    result = evaluate_rule(profile(), rule(RuleType.AGE, "age", RuleOperator.EQUALS, "eighteen", rule_id="invalid"))
    assert result.status == ValueState.INVALID


def test_deterministic_result():
    rules = [rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18)]
    first = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", rules).model_dump()
    second = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", rules).model_dump()
    assert first == second


def test_pass_plus_not_applicable_is_eligible_and_high_confidence():
    result = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, rule_id="age"),
        rule(RuleType.CUSTOM, "future", RuleOperator.CUSTOM, None, rule_id="future"),
    ], scheme())
    assert result.decision == EligibilityDecision.ELIGIBLE
    assert result.confidence == ConfidenceLevel.HIGH


def test_non_mandatory_fail_does_not_reject():
    result = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, mandatory=False),
    ], scheme())
    assert result.decision == EligibilityDecision.ELIGIBLE


def test_non_mandatory_unknown_does_not_block():
    result = evaluate_eligibility(profile(age=None), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, mandatory=False),
    ], scheme())
    assert result.decision == EligibilityDecision.ELIGIBLE
    assert result.confidence == ConfidenceLevel.MEDIUM


def test_invalid_mandatory_input_is_explicit_invalid():
    result = evaluate_eligibility({"age": -5}, "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18),
    ], scheme())
    assert result.decision == EligibilityDecision.INVALID
    assert result.rules[0].status == ValueState.INVALID


def test_stale_scheme_reduces_confidence_without_rejecting():
    result = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18),
    ], scheme(date.today() - timedelta(days=366)))
    assert result.decision == EligibilityDecision.ELIGIBLE
    assert result.confidence == ConfidenceLevel.MEDIUM
    assert result.verification_warnings


def test_official_source_wins_over_lower_priority_conflicting_rule():
    lower = rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 30, rule_id="admin")
    lower.source_type = "VERIFIED_ADMIN"
    official = rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, rule_id="official")
    result = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", [lower, official], scheme())
    assert result.decision == EligibilityDecision.ELIGIBLE
    assert len(result.rules) == 1
    assert result.rules[0].rule_id == "official"
    assert result.verification_warnings


def test_same_priority_conflict_is_unknown_not_guessing():
    first = rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18, rule_id="first")
    second = rule(RuleType.AGE, "age", RuleOperator.LESS_THAN, 18, rule_id="second")
    result = evaluate_eligibility(profile(), "DATA_DRIVEN_TEST_SCHEME", [first, second], scheme())
    assert result.decision == EligibilityDecision.NEEDS_VERIFICATION
    assert all(item.status == ValueState.UNKNOWN for item in result.rules)


def test_confidence_does_not_override_not_eligible():
    result = evaluate_eligibility(profile(age=16), "DATA_DRIVEN_TEST_SCHEME", [
        rule(RuleType.AGE, "age", RuleOperator.GREATER_THAN_OR_EQUAL, 18),
    ], scheme())
    assert result.decision == EligibilityDecision.NOT_ELIGIBLE
    assert result.confidence == ConfidenceLevel.HIGH
