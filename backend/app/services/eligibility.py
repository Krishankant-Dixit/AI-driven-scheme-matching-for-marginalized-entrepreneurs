import math
from datetime import date, timedelta
from typing import Any

from app.schemas.common import ValueState
from app.schemas.eligibility import (
    EligibilityDecision,
    EligibilityResult,
    EligibilitySummary,
    RuleEvaluation,
    ConfidenceLevel,
)
from app.schemas.profile import ProfileCreate
from app.schemas.rule import RuleOperator, RuleType, SchemeRule
from app.schemas.scheme import SchemeRecord

_MISSING = object()
_NUMERIC_RULE_TYPES = {
    RuleType.AGE,
    RuleType.INCOME,
    RuleType.INVESTMENT,
    RuleType.LOAN_REQUIREMENT,
}
_SOURCE_PRIORITY = {
    "OFFICIAL_GOVERNMENT": 5,
    "OFFICIAL_PORTAL": 5,
    "VERIFIED_ADMIN": 4,
    "AI_EXTRACTED": 2,
    "AI_INFERRED": 1,
}


def _enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _profile_values(profile: ProfileCreate | dict[str, Any]) -> dict[str, Any]:
    if isinstance(profile, ProfileCreate):
        return profile.model_dump(mode="json")
    return profile


def _get_rule_value(profile: ProfileCreate | dict[str, Any], rule: SchemeRule) -> Any:
    values = _profile_values(profile)
    if rule.field in values:
        return values[rule.field]
    if rule.rule_type in {RuleType.NEW_ENTERPRISE, RuleType.EXISTING_BUSINESS}:
        return values.get("business_stage", _MISSING)
    if rule.rule_type == RuleType.LOCATION and rule.field in {"location", "state_or_district"}:
        return values.get("state", _MISSING)
    return _MISSING


def _display_field(field: str) -> str:
    return field.replace("_", " ")


def _is_missing(value: Any) -> bool:
    return value is _MISSING or value is None or value == "" or value == "UNKNOWN"


def _invalid_numeric(value: Any) -> bool:
    return isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0


def _invalid_expected(rule: SchemeRule) -> bool:
    expected = rule.expected_value
    if rule.operator in {RuleOperator.REQUIRED, RuleOperator.EXISTS}:
        return expected is not None and not isinstance(expected, bool)
    if rule.operator in {RuleOperator.IN, RuleOperator.NOT_IN, RuleOperator.ANY_OF, RuleOperator.ALL_OF}:
        return not isinstance(expected, list)
    if rule.operator == RuleOperator.BETWEEN:
        return not isinstance(expected, list) or len(expected) != 2 or any(_invalid_numeric(item) for item in expected)
    if rule.rule_type in _NUMERIC_RULE_TYPES and rule.operator in {
        RuleOperator.EQUALS,
        RuleOperator.NOT_EQUALS,
        RuleOperator.GREATER_THAN,
        RuleOperator.GREATER_THAN_OR_EQUAL,
        RuleOperator.LESS_THAN,
        RuleOperator.LESS_THAN_OR_EQUAL,
    }:
        return _invalid_numeric(expected)
    return False


def _compare(value: Any, operator: RuleOperator, expected: Any) -> ValueState:
    try:
        if operator in {RuleOperator.REQUIRED, RuleOperator.EXISTS}:
            return ValueState.PASS
        if operator == RuleOperator.EQUALS:
            return ValueState.PASS if value == expected else ValueState.FAIL
        if operator == RuleOperator.NOT_EQUALS:
            return ValueState.PASS if value != expected else ValueState.FAIL
        if operator == RuleOperator.IN:
            return ValueState.PASS if isinstance(expected, list) and value in expected else ValueState.FAIL
        if operator == RuleOperator.NOT_IN:
            return ValueState.PASS if isinstance(expected, list) and value not in expected else ValueState.FAIL
        if operator == RuleOperator.CONTAINS:
            return ValueState.PASS if expected in value else ValueState.FAIL
        if operator == RuleOperator.NOT_CONTAINS:
            return ValueState.PASS if expected not in value else ValueState.FAIL
        if operator == RuleOperator.BETWEEN:
            if not isinstance(expected, list) or len(expected) != 2:
                return ValueState.INVALID
            return ValueState.PASS if expected[0] <= value <= expected[1] else ValueState.FAIL
        if operator == RuleOperator.ANY_OF:
            if not isinstance(expected, list):
                return ValueState.INVALID
            values = value if isinstance(value, list) else [value]
            return ValueState.PASS if any(item in expected for item in values) else ValueState.FAIL
        if operator == RuleOperator.ALL_OF:
            if not isinstance(expected, list) or not isinstance(value, list):
                return ValueState.INVALID
            return ValueState.PASS if all(item in value for item in expected) else ValueState.FAIL
        if operator == RuleOperator.GREATER_THAN:
            return ValueState.PASS if value > expected else ValueState.FAIL
        if operator == RuleOperator.GREATER_THAN_OR_EQUAL:
            return ValueState.PASS if value >= expected else ValueState.FAIL
        if operator == RuleOperator.LESS_THAN:
            return ValueState.PASS if value < expected else ValueState.FAIL
        if operator == RuleOperator.LESS_THAN_OR_EQUAL:
            return ValueState.PASS if value <= expected else ValueState.FAIL
    except (TypeError, ValueError):
        return ValueState.INVALID
    return ValueState.INVALID


def evaluate_rule(profile: ProfileCreate | dict[str, Any], rule: SchemeRule) -> RuleEvaluation:
    user_value = _get_rule_value(profile, rule)
    base = {
        "rule_id": rule.rule_id,
        "rule_type": rule.rule_type,
        "field": rule.field,
        "mandatory": rule.mandatory,
        "user_value": None if user_value is _MISSING else user_value,
        "expected_value": rule.expected_value,
        "source": rule.source,
        "source_type": rule.source_type.value,
    }

    if rule.mandatory and _enum_value(rule.source_type) == "AI_INFERRED":
        return RuleEvaluation(**base, status=ValueState.INVALID, message="The provided mandatory rule is invalid because AI-inferred data cannot define it.")
    if rule.operator == RuleOperator.CUSTOM:
        return RuleEvaluation(**base, status=ValueState.NOT_APPLICABLE, message="This requirement does not apply because no evaluator is defined for it.")
    if _invalid_expected(rule):
        return RuleEvaluation(**base, status=ValueState.INVALID, message="The rule configuration is invalid and must be corrected.")
    if _is_missing(user_value):
        return RuleEvaluation(**base, status=ValueState.UNKNOWN, message="This requirement cannot be verified because the required information is missing.")
    if rule.rule_type in _NUMERIC_RULE_TYPES and _invalid_numeric(user_value):
        return RuleEvaluation(**base, status=ValueState.INVALID, message="The provided information is invalid and must be corrected.")
    status = _compare(user_value, rule.operator, rule.expected_value)
    messages = {
        ValueState.PASS: "Your profile satisfies this requirement.",
        ValueState.FAIL: "Your profile does not satisfy this mandatory requirement." if rule.mandatory else "Your profile does not satisfy this optional requirement.",
        ValueState.INVALID: "The provided information is invalid and must be corrected.",
    }
    return RuleEvaluation(**base, status=status, message=messages[status])


def _rule_priority(rule: SchemeRule) -> tuple[int, int]:
    source_type = getattr(rule.source_type, "value", rule.source_type)
    verification_status = getattr(rule.verification_status, "value", rule.verification_status)
    return (
        _SOURCE_PRIORITY.get(source_type, 0),
        1 if verification_status == "VERIFIED" else 0,
    )


def _resolve_conflicts(rules: list[SchemeRule]) -> tuple[list[SchemeRule], list[str], set[str]]:
    selected: list[SchemeRule] = []
    warnings: list[str] = []
    unresolved_fields: set[str] = set()
    groups: dict[tuple[RuleType, str], list[SchemeRule]] = {}
    for rule in rules:
        groups.setdefault((rule.rule_type, rule.field), []).append(rule)
    for group in groups.values():
        if len(group) == 1:
            selected.extend(group)
            continue
        highest = max(_rule_priority(rule) for rule in group)
        candidates = [rule for rule in group if _rule_priority(rule) == highest]
        configurations = {(rule.operator, repr(rule.expected_value)) for rule in candidates}
        if len(configurations) > 1:
            selected.extend(candidates)
            unresolved_fields.add(candidates[0].field)
            warnings.append(f"Conflicting rules for {candidates[0].field} could not be safely resolved.")
        else:
            selected.append(candidates[0])
            if len(group) != len(candidates):
                warnings.append(f"A lower-priority rule for {candidates[0].field} was ignored in favor of a higher-priority source.")
    return selected, warnings, unresolved_fields


def _scheme_metadata(scheme: SchemeRecord | dict[str, Any] | None) -> tuple[bool, list[str]]:
    if scheme is None:
        return False, ["Scheme verification metadata was not provided."]
    last_verified = scheme.last_verified if isinstance(scheme, SchemeRecord) else scheme.get("last_verified")
    active = scheme.active if isinstance(scheme, SchemeRecord) else scheme.get("active")
    source_type = _enum_value(scheme.source_type) if isinstance(scheme, SchemeRecord) else scheme.get("source_type")
    warnings: list[str] = []
    if not last_verified or not active or source_type not in {"OFFICIAL_GOVERNMENT", "OFFICIAL_PORTAL"}:
        warnings.append("Scheme verification metadata is incomplete.")
        return False, warnings
    if isinstance(last_verified, str):
        try:
            last_verified = date.fromisoformat(last_verified)
        except ValueError:
            return False, ["Scheme verification metadata contains an invalid date."]
    if last_verified < date.today() - timedelta(days=365):
        warnings.append("Scheme data is stale and should be re-verified.")
        return False, warnings
    return True, warnings


def _confidence(
    decision: EligibilityDecision,
    evaluations: list[RuleEvaluation],
    warnings: list[str],
    scheme_is_fresh: bool,
) -> ConfidenceLevel:
    mandatory = [item for item in evaluations if item.mandatory]
    mandatory_unknown = sum(item.status == ValueState.UNKNOWN for item in mandatory)
    unknown = sum(item.status == ValueState.UNKNOWN for item in evaluations)
    invalid = sum(item.status == ValueState.INVALID for item in evaluations)
    if decision == EligibilityDecision.INVALID or invalid:
        return ConfidenceLevel.LOW
    if mandatory_unknown or unknown > 1 or not scheme_is_fresh:
        return ConfidenceLevel.LOW if unknown > 1 or invalid else ConfidenceLevel.MEDIUM
    if warnings or unknown:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.HIGH


def evaluate_eligibility(
    profile: ProfileCreate | dict[str, Any],
    scheme_id: str,
    rules: list[SchemeRule],
    scheme: SchemeRecord | dict[str, Any] | None = None,
) -> EligibilityResult:
    active_rules, conflict_warnings, unresolved_fields = _resolve_conflicts(rules)
    evaluations = [evaluate_rule(profile, rule) for rule in active_rules]
    for index, rule in enumerate(active_rules):
        if rule.field in unresolved_fields:
            evaluations[index].status = ValueState.UNKNOWN
            evaluations[index].message = "This requirement cannot be verified because conflicting rule sources were found."
    mandatory = [evaluation for evaluation in evaluations if evaluation.mandatory]
    statuses = [evaluation.status for evaluation in evaluations]
    summary = EligibilitySummary(
        total_rules=len(evaluations),
        passed=statuses.count(ValueState.PASS),
        failed=statuses.count(ValueState.FAIL),
        unknown=statuses.count(ValueState.UNKNOWN),
        not_applicable=statuses.count(ValueState.NOT_APPLICABLE),
        invalid=statuses.count(ValueState.INVALID),
    )
    scheme_is_fresh, metadata_warnings = _scheme_metadata(scheme)
    warnings = conflict_warnings + metadata_warnings
    if any(item.status == ValueState.INVALID for item in mandatory):
        decision = EligibilityDecision.INVALID
    elif any(item.status == ValueState.FAIL for item in mandatory):
        decision = EligibilityDecision.NOT_ELIGIBLE
    elif any(item.status == ValueState.UNKNOWN for item in mandatory):
        decision = EligibilityDecision.NEEDS_VERIFICATION
    else:
        decision = EligibilityDecision.ELIGIBLE
    return EligibilityResult(
        scheme_id=scheme_id,
        decision=decision,
        confidence=_confidence(decision, evaluations, warnings, scheme_is_fresh),
        rules=evaluations,
        summary=summary,
        verification_warnings=warnings,
    )
