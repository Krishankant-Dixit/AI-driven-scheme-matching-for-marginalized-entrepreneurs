import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.rule import SchemeRule
from app.schemas.scheme import SchemeRecord
from app.utils.scheme_data import load_rule_seed, load_scheme_seed


def test_seed_data_loads_with_unique_scheme_ids() -> None:
    schemes = load_scheme_seed()
    rules = load_rule_seed()

    assert len(schemes.schemes) == 5
    assert len({scheme.scheme_id for scheme in schemes.schemes}) == 5
    assert len(rules.rules) >= 2


def test_scheme_can_omit_optional_fields() -> None:
    scheme = SchemeRecord(
        scheme_id="TEST",
        name="Test scheme",
        short_name="TEST",
        description="A valid minimal scheme record.",
        official_source="Test source",
        official_source_url="https://example.gov.in/scheme",
        source_type="OFFICIAL_GOVERNMENT",
        last_verified="2026-09-09",
        version="1.0.0",
        active=True,
    )

    assert scheme.income_rule is None
    assert scheme.documents_required == []


@pytest.mark.parametrize(
    ("field", "value"),
    [("rule_type", "NOT_A_RULE"), ("verification_status", "NOT_VERIFIED")],
)
def test_invalid_rule_enum_is_rejected(field: str, value: str) -> None:
    rule_data = {
        "rule_id": "TEST-001",
        "scheme_id": "TEST",
        "rule_type": "AGE",
        "field": "age",
        "operator": "GREATER_THAN_OR_EQUAL",
        "expected_value": 18,
        "mandatory": True,
        "source": "official source",
        "verification_status": "VERIFIED",
        "source_type": "OFFICIAL_GOVERNMENT",
    }
    rule_data[field] = value

    with pytest.raises(ValidationError):
        SchemeRule.model_validate(rule_data)


def test_invalid_url_is_rejected() -> None:
    with pytest.raises(ValidationError):
        SchemeRecord(
            scheme_id="TEST",
            name="Test scheme",
            short_name="TEST",
            description="Invalid URL test.",
            official_source="Test source",
            official_source_url="not-a-url",
            source_type="OFFICIAL_GOVERNMENT",
            last_verified="2026-09-09",
            version="1.0.0",
            active=True,
        )


def test_duplicate_scheme_id_is_rejected(tmp_path: Path) -> None:
    payload = {"schemes": [
        {
            "scheme_id": "DUPLICATE",
            "name": "One",
            "short_name": "ONE",
            "description": "First",
            "official_source": "Source",
            "official_source_url": "https://example.gov.in/one",
            "source_type": "OFFICIAL_GOVERNMENT",
            "last_verified": "2026-09-09",
            "version": "1.0.0",
            "active": True,
        },
        {
            "scheme_id": "DUPLICATE",
            "name": "Two",
            "short_name": "TWO",
            "description": "Second",
            "official_source": "Source",
            "official_source_url": "https://example.gov.in/two",
            "source_type": "OFFICIAL_GOVERNMENT",
            "last_verified": "2026-09-09",
            "version": "1.0.0",
            "active": True,
        },
    ]}
    path = tmp_path / "schemes.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="unique"):
        load_scheme_seed(path)


def test_unknown_eligibility_information_is_preserved() -> None:
    schemes = load_scheme_seed()
    pmyy = next(scheme for scheme in schemes.schemes if scheme.scheme_id == "PMMY")
    rules = load_rule_seed()
    pmyy_rule = next(rule for rule in rules.rules if rule.scheme_id == "PMMY")

    assert pmyy.loan_rule["state"] == "UNKNOWN"
    assert pmyy_rule.verification_status == "UNKNOWN"


def test_multiple_rules_can_belong_to_one_scheme() -> None:
    rules = load_rule_seed()
    rules_for_pmegp = [rule for rule in rules.rules if rule.scheme_id == "PMEGP"]

    assert len(rules_for_pmegp) == 2
