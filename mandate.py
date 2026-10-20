"""Lab 13: check the fictional Meridian mandate; standard library only.

AI-assisted implementation. Run: python mandate.py
Weights are percentage points (2 means 2%), not decimal fractions.
"""

import math


# Editable inputs: holding -> (issuer, business days to redeem, reserve-eligible).
HOLDINGS = {
    "Cash": ("none", 0, True),
    "Treasury bills": ("U.S. Treasury", 1, True),
    "Treasury 10-year note": ("U.S. Treasury", 1, True),
    "Global equity index fund": ("diversified fund", 2, False),
    "Investment-grade bond fund": ("diversified fund", 3, False),
    "Private real estate fund": ("diversified fund", 90, False),
    "Acme Corp bonds": ("Acme Corp", 4, False),
    "Acme Corp stock": ("Acme Corp", 1, False),
}

CANDIDATES = {
    "A": {
        "Cash": 2, "Treasury bills": 2, "Treasury 10-year note": 10,
        "Global equity index fund": 60, "Investment-grade bond fund": 26,
        "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0,
    },
    "B": {
        "Cash": 1, "Treasury bills": 0, "Treasury 10-year note": 0,
        "Global equity index fund": 55, "Investment-grade bond fund": 20,
        "Private real estate fund": 15, "Acme Corp bonds": 5, "Acme Corp stock": 4,
    },
    "C": {
        "Cash": 1, "Treasury bills": 1, "Treasury 10-year note": 0,
        "Global equity index fund": 70, "Investment-grade bond fund": 20,
        "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 8,
    },
    # AI-proposed counterexample, not an optimized allocation or recommendation.
    "D": {
        "Cash": 100, "Treasury bills": 0, "Treasury 10-year note": 0,
        "Global equity index fund": 0, "Investment-grade bond fund": 0,
        "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0,
    },
    # Lab 14: the client's S4 benchmark, checked against its own mandate.
    "E": {
        "Cash": 0, "Treasury bills": 0, "Treasury 10-year note": 0,
        "Global equity index fund": 60, "Investment-grade bond fund": 40,
        "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0,
    },
}

RESERVE_SIZE_MILLIONS = 100
QUARTERLY_DISTRIBUTION_MILLIONS = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW_DAYS = 5
MINIMUM_LIQUID_SHARE_PERCENT = 90
ISSUER_LIMIT_PERCENT = 8
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}


def reserve_minimum_percent():
    """Convert required payouts in USD millions to a portfolio percentage."""
    if not math.isfinite(RESERVE_SIZE_MILLIONS) or RESERVE_SIZE_MILLIONS <= 0:
        raise ValueError("Reserve size must be finite and positive.")
    if not math.isfinite(QUARTERLY_DISTRIBUTION_MILLIONS) or QUARTERLY_DISTRIBUTION_MILLIONS < 0:
        raise ValueError("Quarterly distribution must be finite and nonnegative.")
    if not isinstance(QUARTERS_TO_COVER, int) or QUARTERS_TO_COVER < 0:
        raise ValueError("Quarters to cover must be a nonnegative integer.")
    return QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION_MILLIONS / RESERVE_SIZE_MILLIONS * 100


def check_candidate(weights):
    """Return (rule, measured percentage, pass flag) for the five checks."""
    if not HOLDINGS or set(weights) != set(HOLDINGS):
        raise ValueError("Each candidate must list every holding exactly once; use 0 for unused holdings.")
    if not all(math.isfinite(weight) for weight in weights.values()):
        raise ValueError("Weights must be finite numbers.")
    if not isinstance(LIQUIDITY_WINDOW_DAYS, int) or LIQUIDITY_WINDOW_DAYS < 0:
        raise ValueError("Liquidity window must be a nonnegative integer.")
    if not 0 <= MINIMUM_LIQUID_SHARE_PERCENT <= 100 or not 0 <= ISSUER_LIMIT_PERCENT <= 100:
        raise ValueError("Percentage limits must be between 0 and 100.")

    reserve_weight = 0.0
    liquid_weight = 0.0
    company_weights = {}
    for holding, weight in weights.items():
        issuer, days, reserve_eligible = HOLDINGS[holding]
        if not isinstance(days, int) or days < 0 or not isinstance(reserve_eligible, bool):
            raise ValueError("Holdings require nonnegative integer redemption days and boolean eligibility.")
        if reserve_eligible:
            reserve_weight += weight
        if days <= LIQUIDITY_WINDOW_DAYS:
            liquid_weight += weight
        if issuer not in EXEMPT_ISSUERS:
            # Combine a company's bonds and stock before checking concentration.
            company_weights[issuer] = company_weights.get(issuer, 0.0) + weight

    total_weight = math.fsum(weights.values())
    lowest_weight = min(weights.values())
    largest_company = max(company_weights.values(), default=0.0)
    minimum_reserve = reserve_minimum_percent()
    return [
        ("Weights sum to 100", total_weight,
         math.isclose(total_weight, 100.0, rel_tol=0.0, abs_tol=1e-9)),
        ("Long-only (lowest weight)", lowest_weight, lowest_weight >= 0),
        (f"Reserve >= {minimum_reserve:.1f}%", reserve_weight, reserve_weight >= minimum_reserve),
        (f"Redeemable in {LIQUIDITY_WINDOW_DAYS} days >= {MINIMUM_LIQUID_SHARE_PERCENT:.1f}%",
         liquid_weight, liquid_weight >= MINIMUM_LIQUID_SHARE_PERCENT),
        (f"Largest single company <= {ISSUER_LIMIT_PERCENT:.1f}%",
         largest_company, largest_company <= ISSUER_LIMIT_PERCENT),
    ]


def main():
    print(f"Reserve minimum: {reserve_minimum_percent():.1f}% of the portfolio")
    for name, weights in CANDIDATES.items():
        print(f"\nCandidate {name}")
        checks = check_candidate(weights)
        for rule, value, passed in checks:
            print(f"{rule}: {value:.1f} {'pass' if passed else 'FAIL'}")
        print("Calendar-year loss: requires CIO clarification")
        failures = sum(not passed for _, _, passed in checks)
        print("passes every checkable rule" if failures == 0 else f"fails {failures} rule(s)")


if __name__ == "__main__":
    main()
