# Eligibility Engine Contract

The Phase 4/5 engine evaluates only structured rules loaded from `data/rules.json`. Scheme IDs select the records to evaluate; they do not select Python branches or special-case logic.

## Precedence

The system precedence is:

```text
P0 data validity
P1 official mandatory eligibility rules
P2 explicit scheme restrictions
P3 verified profile facts
P4 deterministic soft matching
P5 financial compatibility
P6 AI semantic similarity
P7 ranking and personalization
```

Phase 5 implements P0 through P3 for hard eligibility. Future AI or ranking signals cannot alter the result.

Rule sources are prioritized as follows: official verified government/portal data, verified structured data, verified admin data, AI-extracted data, and AI-inferred data. An AI-inferred mandatory rule is invalid. Conflicting same-priority rules are retained as `UNKNOWN` with a verification warning; lower-priority duplicates are ignored in favor of the higher-priority rule.

## Decision and Confidence

Mandatory `FAIL` produces `NOT_ELIGIBLE` even when another rule is `UNKNOWN`. Without a mandatory failure, mandatory `UNKNOWN` produces `NEEDS_VERIFICATION`. Only mandatory `PASS` and `NOT_APPLICABLE` produce `ELIGIBLE`. Mandatory `INVALID` produces an explicit `INVALID` result.

Confidence is separate from eligibility. Fresh, complete, verified data can produce `HIGH`; unknown information or stale/incomplete scheme metadata reduces confidence to `MEDIUM` or `LOW` without changing the decision.