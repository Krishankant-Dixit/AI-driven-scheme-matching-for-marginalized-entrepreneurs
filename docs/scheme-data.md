# Scheme Data Contract

`data/schemes.json` contains scheme metadata and `data/rules.json` contains generic rules. The records are JSON documents so they can later be inserted into MongoDB without changing their field names.

## Adding a Scheme

1. Add one unique `scheme_id` to `schemes.json`.
2. Include the official source URL, source type, verification date, version, and active flag.
3. Add only eligibility facts supported by an authoritative source.
4. Leave optional criteria as `null` or mark rule verification as `UNKNOWN` when evidence is insufficient.
5. Add generic rules keyed by `scheme_id`; do not add scheme-specific branches to Python.

## Source Hierarchy

`OFFICIAL_GOVERNMENT` and `OFFICIAL_PORTAL` are the preferred sources, followed by `VERIFIED_ADMIN`, `AI_EXTRACTED`, and `AI_INFERRED`. AI-inferred information must never be used as a mandatory eligibility fact.

## Rule and Value States

Rules support the generic types listed in `backend/app/schemas/rule.py`. Verification status is independent from a future decision state. The supported decision-state vocabulary is `PASS`, `FAIL`, `UNKNOWN`, `NOT_APPLICABLE`, and `INVALID`; Phase 2 stores this vocabulary but does not evaluate it.