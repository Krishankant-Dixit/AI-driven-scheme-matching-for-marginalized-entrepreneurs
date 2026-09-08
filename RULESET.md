# 📋 Scheme Matching RuleSet

## AI-Driven Scheme Matching for Marginalized Entrepreneurs

**SIH Problem Statement:** SIH26092
**RuleSet Version:** 1.1.0

---

# 1. Purpose

This document defines the rules, precedence order, eligibility evaluation, unknown-value handling, scoring methodology, and recommendation logic used by the **AI-Driven Scheme Matching Engine**.

The system uses a **Hybrid Rule-Based + AI Matching Architecture**.

The fundamental principle is:

> **Rules determine eligibility, AI determines semantic relevance, and ranking determines recommendation priority.**

AI similarity must never override a mandatory eligibility condition.

---

# 2. Decision Pipeline

Every recommendation must follow this pipeline:

```text
User Profile
     ↓
Input Validation
     ↓
Value Normalization
     ↓
Mandatory Eligibility Evaluation
     ↓
Unknown-Value Resolution
     ↓
Hard Eligibility Filtering
     ↓
Soft Matching
     ↓
AI Semantic Matching
     ↓
Weighted Scoring
     ↓
Confidence Calculation
     ↓
Ranking
     ↓
Explanation Generation
```

No later stage may override a decision made by a higher-priority stage.

---

# 3. Rule Precedence

Rules are evaluated in the following **strict order of precedence**:

```text
P0 — System/Data Validity
        ↓
P1 — Official Mandatory Eligibility Rules
        ↓
P2 — Explicit Scheme Restrictions
        ↓
P3 — User Profile Facts
        ↓
P4 — Deterministic Soft Matching
        ↓
P5 — Financial Compatibility
        ↓
P6 — AI Semantic Similarity
        ↓
P7 — Ranking & Personalization
```

### Precedence Principle

> **Higher-priority rules always override lower-priority signals.**

For example:

```text
Official Rule:
Scheme available only to women

User:
Gender = MALE

AI Semantic Similarity:
95%

Final:
NOT_ELIGIBLE
```

The AI score cannot override the mandatory gender restriction.

---

# 4. Rule Priority Definitions

## P0 — Data Validity

Input validation has the highest priority.

Invalid data must not be used for eligibility decisions.

Examples:

```text
Age = -5
Income = "abc"
Investment = "five lakh"
State = null
```

These values must be marked:

```text
INVALID
```

rather than being treated as eligible.

---

# 5. P1 — Official Mandatory Eligibility

Officially documented mandatory conditions have the highest eligibility priority.

Examples:

* Minimum age
* Maximum age
* Mandatory category
* Mandatory gender
* Mandatory location
* Mandatory business stage
* Mandatory enterprise type
* Mandatory income limit
* Mandatory investment/project-cost limit

If a mandatory condition is definitely violated:

```text
Result = NOT_ELIGIBLE
```

---

# 6. P2 — Explicit Scheme Restrictions

Explicit restrictions defined by the scheme are evaluated after mandatory eligibility rules but before AI matching.

Examples:

```text
New enterprise only
Existing business only
Specific sector only
Specific state only
Specific beneficiary group only
```

A confirmed restriction failure results in:

```text
NOT_ELIGIBLE
```

---

# 7. P3 — User Profile Facts

Only user-provided or reliably extracted profile information should be used as factual input.

Example:

```json
{
  "age": 24,
  "gender": "FEMALE",
  "state": "Uttar Pradesh"
}
```

The system must not infer sensitive eligibility attributes without sufficient evidence.

---

# 8. P4 — Deterministic Soft Matching

These rules improve recommendation ranking but normally do not determine eligibility by themselves.

Examples:

```text
Business sector similarity
Location preference
Business-stage relevance
Financial preference
Benefit preference
```

---

# 9. P5 — Financial Compatibility

Financial compatibility considers:

```text
Investment Requirement
Loan Requirement
Project Cost
Loan Range
Subsidy/Assistance Type
```

A financial mismatch becomes `NOT_ELIGIBLE` only when the official scheme explicitly makes the financial condition mandatory.

Otherwise:

```text
Financial Match = LOW
```

and the recommendation score is reduced.

---

# 10. P6 — AI Semantic Similarity

AI/NLP is used for semantic understanding.

Example:

```text
User:
"Small homemade snacks manufacturing business"

Scheme:
"Financial assistance for micro food-processing enterprises"
```

The AI may identify strong semantic relevance.

However:

```text
AI similarity ≠ eligibility
```

AI similarity can increase or decrease ranking but can never override:

* Mandatory age rules
* Mandatory category rules
* Mandatory gender rules
* Mandatory location restrictions
* Mandatory business restrictions
* Mandatory financial restrictions

---

# 11. P7 — Ranking & Personalization

Only schemes that survive mandatory eligibility filtering are ranked.

Example:

```text
Scheme A → 94%
Scheme B → 88%
Scheme C → 81%
```

Ranking does not change eligibility status.

---

# 12. Value States

Every eligibility attribute must have one of these states:

```text
PASS
FAIL
UNKNOWN
NOT_APPLICABLE
INVALID
```

These states must be treated differently.

---

# 13. PASS

`PASS` means the system has sufficient verified information and the condition is satisfied.

Example:

```text
Scheme minimum age = 18
User age = 25

Result:
PASS
```

---

# 14. FAIL

`FAIL` means sufficient information exists and the condition is definitely violated.

Example:

```text
Scheme minimum age = 18
User age = 16

Result:
FAIL
```

For mandatory conditions:

```text
FAIL → NOT_ELIGIBLE
```

---

# 15. UNKNOWN

`UNKNOWN` means the system does not have sufficient reliable information to determine whether the condition passes or fails.

Example:

```text
Scheme:
Annual income must be below ₹3 lakh

User:
Annual income = UNKNOWN
```

Result:

```text
Income = UNKNOWN
```

It must **not** be converted into:

```text
PASS
```

and it must **not** automatically be converted into:

```text
FAIL
```

---

# 16. UNKNOWN Handling Principle

The fundamental rule is:

> **UNKNOWN is not PASS and UNKNOWN is not FAIL.**

The system must preserve uncertainty.

```text
UNKNOWN
   ↓
Need verification
```

rather than:

```text
UNKNOWN
   ↓
Eligible
```

---

# 17. Mandatory Rule + UNKNOWN

If a mandatory eligibility condition is `UNKNOWN`, the system must not claim confirmed eligibility.

Example:

```text
Scheme:
Income ≤ ₹3 lakh

User:
Income = UNKNOWN

Result:
Eligibility = NEEDS_VERIFICATION
```

The scheme may still appear as a recommendation if no mandatory condition has failed.

Recommended status:

```text
POTENTIALLY_ELIGIBLE
```

or:

```text
NEEDS_VERIFICATION
```

depending on the severity of the missing information.

---

# 18. Mandatory Rule + FAIL

If a mandatory condition fails:

```text
FAIL
 ↓
NOT_ELIGIBLE
```

The scheme must not be recommended as an eligible scheme, regardless of AI similarity.

Example:

```text
Mandatory:
Age ≥ 18

User:
Age = 16

AI Similarity:
98%

Final:
NOT_ELIGIBLE
```

---

# 19. Optional Rule + UNKNOWN

If an optional condition is unknown:

```text
UNKNOWN
 ↓
Do not reject
 ↓
Reduce confidence if necessary
```

Example:

```text
Scheme:
Preference for rural businesses

User:
Location Type = UNKNOWN

Result:
No rejection
```

The system can still recommend the scheme based on other available information.

---

# 20. NOT_APPLICABLE

`NOT_APPLICABLE` means the condition does not apply to the current scheme or user.

Example:

```text
Scheme has no gender restriction.

Gender Eligibility:
NOT_APPLICABLE
```

`NOT_APPLICABLE` should not reduce the eligibility score.

---

# 21. INVALID

`INVALID` means the supplied value is malformed or impossible to interpret.

Examples:

```text
Age = -10
Income = "hello"
Investment = "-5000"
```

Invalid data must not be silently converted to `UNKNOWN`.

Instead:

```text
INVALID
 ↓
Request correction
```

Example:

> Please enter a valid annual income.

---

# 22. Three-Valued Eligibility Logic

For mandatory rules, the system effectively uses:

```text
TRUE
FALSE
UNKNOWN
```

Logic:

| Condition                         | Result             |
| --------------------------------- | ------------------ |
| All mandatory rules = TRUE        | ELIGIBLE           |
| Any mandatory rule = FALSE        | NOT_ELIGIBLE       |
| No FALSE but at least one UNKNOWN | NEEDS_VERIFICATION |

Formally:

```text
IF any mandatory condition = FAIL
    → NOT_ELIGIBLE

ELSE IF any mandatory condition = UNKNOWN
    → NEEDS_VERIFICATION

ELSE
    → ELIGIBLE
```

---

# 23. Complete Eligibility State Machine

```text
                  ┌──────────────┐
                  │ Start Check  │
                  └──────┬───────┘
                         ↓
                ┌─────────────────┐
                │ Invalid Input?  │
                └──────┬──────────┘
                   YES │   NO
                       ↓
                    INVALID
                       │
                       ▼
                  Fix Information


NO
 ↓
Evaluate Mandatory Rules
        │
        ├──── FAIL ────→ NOT_ELIGIBLE
        │
        ├── UNKNOWN ────→ NEEDS_VERIFICATION
        │
        └──── PASS ─────→ Continue
                              ↓
                        Soft Matching
                              ↓
                         AI Matching
                              ↓
                           Ranking
```

---

# 24. Unknown Information and Scoring

Unknown values must not receive a full score.

Example:

```text
Income Match = UNKNOWN
```

must not become:

```text
Income Match = 100
```

Instead, the scoring system should use one of these approaches:

### Approach A — Score Exclusion

Remove the unknown criterion from the denominator.

```text
Score =
sum(known criterion scores)
/
sum(weights of known criteria)
```

### Approach B — Neutral Score

Assign a neutral value only when the criterion is explicitly optional.

The recommended implementation is:

> **Use score exclusion for unknown mandatory/important criteria and neutral handling for truly optional criteria.**

---

# 25. Example of Unknown-Aware Scoring

Suppose:

```text
Eligibility = 100
Category = 100
Business = 90
Location = UNKNOWN
Financial = 80
Semantic = 85
```

The system should not simply calculate:

```text
UNKNOWN = 0
```

because that would unfairly punish the user.

Instead, the system calculates the score using known weighted components and separately lowers confidence because information is missing.

---

# 26. Confidence vs Match Score

The system must maintain two separate concepts:

### Match Score

How well the known user information matches the scheme.

### Confidence

How reliable the recommendation is given the available information.

Example:

```text
Match Score: 94%
Confidence: MEDIUM
```

This means:

> The known information matches strongly, but some eligibility information still requires verification.

---

# 27. Confidence Rules

### HIGH

```text
All mandatory information available
+
No mandatory UNKNOWN values
+
Scheme data recently verified
```

### MEDIUM

```text
No mandatory FAIL
+
One or more important UNKNOWN values
```

### LOW

```text
Multiple important UNKNOWN values
OR
Scheme data requires verification
OR
Insufficient profile information
```

---

# 28. Example — HIGH Confidence

```text
Age              PASS
Category         PASS
Gender           PASS
Location         PASS
Business Type    PASS
Income           PASS
Investment       PASS
```

Result:

```text
Eligibility: ELIGIBLE
Confidence: HIGH
```

---

# 29. Example — MEDIUM Confidence

```text
Age              PASS
Category         PASS
Gender           PASS
Location         PASS
Business Type    PASS
Income           UNKNOWN
Investment       PASS
```

Result:

```text
Eligibility:
POTENTIALLY_ELIGIBLE

Confidence:
MEDIUM

Action:
Verify income requirement
```

---

# 30. Example — NOT ELIGIBLE

```text
Age              PASS
Category         FAIL
Gender           PASS
Location         PASS
Business Type    PASS
```

Result:

```text
Eligibility:
NOT_ELIGIBLE
```

AI similarity is ignored for eligibility determination.

---

# 31. AI Override Rule

### STRICT RULE

```text
AI CANNOT OVERRIDE A MANDATORY RULE.
```

Example:

```text
Official Rule:
SC/ST only

User:
GENERAL

AI Semantic Similarity:
97%

Final:
NOT_ELIGIBLE
```

---

# 32. Conflict Resolution

If different data sources provide conflicting information:

```text
Official verified scheme rule
        >
Verified structured database
        >
Administrator-entered rule
        >
AI-extracted information
        >
AI-generated inference
```

The higher-priority source wins.

AI-generated inference must never override verified structured data.

---

# 33. Scheme Data Freshness

Every scheme must have:

```json
{
  "last_verified": "2026-09-01",
  "source_type": "OFFICIAL",
  "source_url": "OFFICIAL_SOURCE"
}
```

If scheme information is outdated:

```text
Data Status = STALE
```

The system should reduce confidence and display:

> Scheme information may require verification.

---

# 34. Official Source Priority

Scheme information should follow this priority:

```text
1. Official Central Government Portal
2. Official State Government Portal
3. Official Government Department
4. Official Implementing Agency
5. Other authoritative source
6. Secondary source
```

Secondary sources should not override official information.

---

# 35. Missing Scheme Data

If a scheme does not have sufficient eligibility information:

```text
Scheme Status:
INCOMPLETE
```

It should not be presented as a confidently eligible recommendation.

Possible result:

```text
NEEDS_VERIFICATION
```

---

# 36. Recommendation Status

Every recommended scheme must have one final status:

```text
ELIGIBLE
POTENTIALLY_ELIGIBLE
NEEDS_VERIFICATION
LOW_RELEVANCE
NOT_ELIGIBLE
```

---

# 37. Final Decision Matrix

| Mandatory Rules | Unknowns | Result                    |
| --------------- | -------: | ------------------------- |
| All PASS        |        0 | ELIGIBLE                  |
| All PASS        |       ≥1 | NEEDS_VERIFICATION        |
| Any FAIL        |      Any | NOT_ELIGIBLE              |
| Invalid input   |      Any | INPUT_CORRECTION_REQUIRED |

---

# 38. Recommendation Eligibility

Only the following statuses can normally appear in the main recommendation list:

```text
ELIGIBLE
POTENTIALLY_ELIGIBLE
NEEDS_VERIFICATION
```

`NOT_ELIGIBLE` schemes should normally be excluded from the primary recommendation list.

They may optionally be shown under:

> **Why other schemes were not recommended**

---

# 39. Explanation Rules

Every recommendation must explain:

### Positive Reasons

```text
✓ Age requirement satisfied
✓ Business sector matches
✓ Location is supported
✓ Financial requirement is compatible
```

### Unknown Conditions

```text
⚠ Income requirement could not be verified
```

### Failed Conditions

For excluded schemes:

```text
✗ Required category does not match
```

---

# 40. Never Hide UNKNOWN

The system must not hide missing information merely to increase the match score.

Bad:

```text
Match Score: 95%
```

when several mandatory attributes are unknown.

Better:

```text
Match Score: 95%
Confidence: MEDIUM

⚠ Income eligibility requires verification.
```

---

# 41. Example Complete Evaluation

### User

```json
{
  "age": 25,
  "gender": "FEMALE",
  "category": "OBC",
  "state": "Uttar Pradesh",
  "location_type": "RURAL",
  "business_type": "MANUFACTURING",
  "business_stage": "NEW",
  "income": 250000,
  "investment": 500000
}
```

### Scheme

```text
Minimum Age: 18
Categories: OBC, SC, ST, GENERAL
Locations: Rural, Urban
Business: Manufacturing
Business Stage: New
Maximum Income: ₹300,000
```

### Evaluation

```text
Age             → PASS
Gender          → NOT_APPLICABLE
Category        → PASS
State           → PASS
Location        → PASS
Business        → PASS
Business Stage  → PASS
Income          → PASS
Investment      → PASS
```

Final:

```text
Eligibility: ELIGIBLE
Confidence: HIGH
```

---

# 42. Example with UNKNOWN

### User

```text
Age: 25
Category: OBC
State: Uttar Pradesh
Income: UNKNOWN
Business: Manufacturing
```

### Scheme

```text
Maximum Income: ₹300,000
```

Evaluation:

```text
Age             → PASS
Category        → PASS
State           → PASS
Business        → PASS
Income          → UNKNOWN
```

Final:

```text
Eligibility:
NEEDS_VERIFICATION

Confidence:
MEDIUM
```

Explanation:

```text
✓ Age requirement satisfied
✓ Category supported
✓ Business type matches
✓ State is supported

⚠ Income requirement could not be verified.
```

---

# 43. Example with FAIL + UNKNOWN

```text
Age:
PASS

Category:
FAIL

Income:
UNKNOWN
```

Final:

```text
NOT_ELIGIBLE
```

Reason:

```text
✗ Applicant category does not satisfy the mandatory requirement.
```

The income `UNKNOWN` does not change the final decision because a mandatory condition has already failed.

---

# 44. Deterministic Before AI

The engine must always execute:

```text
Rules
 ↓
Eligibility
 ↓
AI
```

and never:

```text
AI
 ↓
Eligibility
```

This ensures explainability and prevents hallucinated eligibility.

---

# 45. Pseudocode

```python
def evaluate_scheme(user, scheme):

    # P0: Validate input
    validation = validate_user(user)

    if validation.invalid:
        return "INPUT_CORRECTION_REQUIRED"

    # P1/P2: Mandatory rules
    results = evaluate_mandatory_rules(user, scheme)

    # Any mandatory failure has absolute priority
    if any(r == "FAIL" for r in results):
        return {
            "status": "NOT_ELIGIBLE",
            "confidence": "HIGH"
        }

    # Unknown mandatory conditions
    has_unknown = any(
        r == "UNKNOWN"
        for r in results
    )

    # P4/P5/P6: Soft + AI matching
    soft_score = calculate_soft_match(user, scheme)
    semantic_score = calculate_semantic_similarity(user, scheme)

    score = calculate_weighted_score(
        user,
        scheme,
        soft_score,
        semantic_score
    )

    confidence = calculate_confidence(
        results,
        scheme.last_verified
    )

    if has_unknown:
        status = "NEEDS_VERIFICATION"
    else:
        status = "ELIGIBLE"

    return {
        "status": status,
        "score": score,
        "confidence": confidence
    }
```

---

# 46. Ranking Rule

Ranking must occur only after eligibility evaluation.

```python
eligible_schemes = [
    s for s in schemes
    if s.status != "NOT_ELIGIBLE"
]

eligible_schemes.sort(
    key=lambda x: x["score"],
    reverse=True
)
```

If two schemes have the same score:

```text
1. Higher confidence
2. Higher mandatory-rule completeness
3. Higher business relevance
4. Newer verification date
```

---

# 47. Recommendation Output

Recommended API response:

```json
{
  "scheme": "Example Scheme",
  "status": "NEEDS_VERIFICATION",
  "match_score": 91,
  "confidence": "MEDIUM",

  "matched_rules": [
    "Age",
    "Category",
    "Business Type",
    "Location"
  ],

  "unknown_rules": [
    "Annual Income"
  ],

  "failed_rules": [],

  "reasons": [
    "Business sector matches",
    "Applicant category is supported",
    "Location is supported"
  ],

  "verification_required": [
    "Annual income eligibility"
  ]
}
```

---

# 48. Core Safety Guarantees

The matching engine guarantees:

```text
✓ Mandatory FAIL always overrides AI similarity
✓ UNKNOWN is never silently treated as PASS
✓ INVALID values require correction
✓ AI cannot invent eligibility
✓ AI cannot override official rules
✓ Outdated scheme data reduces confidence
✓ Recommendations include explanations
✓ Final government approval remains outside the system
```

---

# 49. Golden Rule

> **FAIL beats UNKNOWN. UNKNOWN beats ASSUMPTION. OFFICIAL RULES beat AI.**

In operational terms:

```text
MANDATORY FAIL
      ↓
NOT_ELIGIBLE

NO FAIL + UNKNOWN
      ↓
NEEDS_VERIFICATION

ALL MANDATORY PASS
      ↓
ELIGIBLE

AI SCORE
      ↓
ONLY RANKS THE RESULT
```

---

# 50. Version

```text
RULESET_VERSION = 1.1.0

Project:
AI-Driven Scheme Matching for Marginalized Entrepreneurs

SIH:
SIH26092

Status:
SIH 2026 Prototype

Last Updated:
2026-09-09
```

---

## Final Architecture Principle

```text
                 OFFICIAL SCHEME DATA
                         │
                         ▼
                ┌─────────────────┐
                │ Mandatory Rules │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
             FAIL                 PASS/UNKNOWN
              │                     │
              ▼                     ▼
       NOT_ELIGIBLE          Unknown Handling
                                    │
                                    ▼
                            Soft Matching + AI
                                    │
                                    ▼
                              Match Score
                                    │
                                    ▼
                              Confidence
                                    │
                                    ▼
                               Ranking
                                    │
                                    ▼
                             Explanation
```

> **The system is designed to be conservative about eligibility and intelligent about relevance.**
