# Phase 6 Matching Engine

Phase 6 calculates a deterministic match assessment after the Phase 5 hard eligibility result. Eligibility, match score, and confidence remain separate values.

## Eligibility Gate

`NOT_ELIGIBLE` sets `eligible_for_matching` to `false` and leaves `deterministic_match_score` null. `NEEDS_VERIFICATION` may be scored, but its eligibility status remains visible. `ELIGIBLE` is scored normally.

## Dimensions and Weights

The configured planned weights are category 20, business 30, location 10, financial 15, and business stage 10. These deterministic dimensions total 85. The remaining semantic weight is reserved at 15 for Phase 7 and is never fabricated in Phase 6.

The score is normalized over applicable dimensions only:

```text
deterministic_match_score =
sum(dimension_score * dimension_weight) /
sum(applicable_dimension_weight)
```

`UNKNOWN` and `NOT_APPLICABLE` dimensions are excluded from the denominator. Unknown dimensions are reported and reduce confidence; they are never treated as zero or full points. If no dimension is applicable, the score is null.

## Structured Matching

Category, business, location, financial, and business-stage matching use only structured profile and scheme fields. No text similarity, AI, embeddings, ranking, or scheme-specific Python branches are used. Missing scheme criteria produce `NOT_APPLICABLE`; missing profile facts produce `UNKNOWN`.

`semantic_score` and `final_match_score` remain null until Phase 7.