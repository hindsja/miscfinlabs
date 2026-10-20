"""Lab 14 Meridian portfolio baselines using course-authored training inputs.

Run: python portfolio.py
Returns and volatilities are annual decimal fractions (0.035 means 3.5%).
"""

import math


# Editable course-authored training values; these are not market estimates.
SLEEVES = {
    "Treasury bills": {"return": 0.035, "volatility": 0.005},
    "Treasury 10-year note": {"return": 0.043, "volatility": 0.070},
    "Investment-grade bond fund": {"return": 0.050, "volatility": 0.060},
    "Global equity index fund": {"return": 0.080, "volatility": 0.160},
}

# Rows and columns follow SLEEVES order. Edit both matching cells together.
CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]

# CPI of 2.5% is an estimate; the mandate's objective is CPI + 4%.
OBJECTIVE_RETURN = 0.065
RESERVE_ELIGIBLE = ("Treasury bills", "Treasury 10-year note")


def validate_inputs(sleeves, correlations, objective):
    """Reject invalid inputs before calculating any portfolio."""
    names = list(sleeves)
    if not names or len(correlations) != len(names) or any(
        len(row) != len(names) for row in correlations
    ):
        raise ValueError("Correlation table must be square with one row per sleeve.")
    if not math.isfinite(objective):
        raise ValueError("Objective return must be finite.")
    for name, values in sleeves.items():
        expected_return = values["return"]
        volatility = values["volatility"]
        if not math.isfinite(expected_return) or not math.isfinite(volatility):
            raise ValueError(f"Return and volatility must be finite for {name}.")
        if volatility <= 0:
            raise ValueError(f"Volatility must be positive for {name}.")
    for i, row in enumerate(correlations):
        for j, value in enumerate(row):
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError(f"Correlation for {names[i]} and {names[j]} must be between -1 and 1.")
            if not math.isclose(value, correlations[j][i], rel_tol=0, abs_tol=1e-12):
                raise ValueError(f"Correlation table is not symmetric for {names[i]} and {names[j]}.")
        if not math.isclose(row[i], 1.0, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"Self-correlation for {names[i]} must equal 1.")


def covariance_matrix(sleeves, correlations):
    """Return covariance[i][j] = correlation[i][j] * vol[i] * vol[j]."""
    names = list(sleeves)
    return [
        [correlations[i][j] * sleeves[names[i]]["volatility"] * sleeves[names[j]]["volatility"]
         for j in range(len(names))]
        for i in range(len(names))
    ]


def benchmark_weights(sleeves):
    """Return Meridian's 40% investment-grade bond, 60% equity benchmark."""
    return {name: (0.40 if name == "Investment-grade bond fund" else
                   0.60 if name == "Global equity index fund" else 0.0)
            for name in sleeves}


def equal_weights(sleeves):
    """Allocate equally across all sleeves."""
    return {name: 1.0 / len(sleeves) for name in sleeves}


def inverse_volatility_weights(sleeves):
    """Allocate in proportion to each sleeve's inverse volatility."""
    inverse = {name: 1.0 / values["volatility"] for name, values in sleeves.items()}
    total = math.fsum(inverse.values())
    return {name: value / total for name, value in inverse.items()}


def validate_weights(weights, sleeves):
    """Require one finite, nonnegative weight per sleeve, summing to one."""
    if set(weights) != set(sleeves):
        raise ValueError("Portfolio weights must cover every sleeve exactly once.")
    if any(not math.isfinite(value) or value < 0 for value in weights.values()):
        raise ValueError("Portfolio weights must be finite and nonnegative.")
    if not math.isclose(math.fsum(weights.values()), 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError("Portfolio weights must sum to 100%.")


def expected_return(weights, sleeves):
    """Weighted average of the sleeves' expected annual returns."""
    return math.fsum(weights[name] * sleeves[name]["return"] for name in sleeves)


def portfolio_variance(weights, covariance, names):
    """Compute sum_i sum_j weight_i * weight_j * covariance_ij."""
    return math.fsum(
        weights[names[i]] * weights[names[j]] * covariance[i][j]
        for i in range(len(names)) for j in range(len(names))
    )


def portfolio_volatility(weights, covariance, names):
    """Annual portfolio standard deviation, including cross-asset covariance."""
    variance = portfolio_variance(weights, covariance, names)
    if variance < -1e-12:
        raise ValueError("Covariance inputs produced negative portfolio variance.")
    return math.sqrt(max(variance, 0.0))


def reserve_eligible_weight(weights):
    """Sum the Lab 13 reserve-eligible Treasury sleeves."""
    return math.fsum(weights[name] for name in RESERVE_ELIGIBLE)


def meets_objective(portfolio_return, objective):
    """Compare expected return with the stated target, before rounding."""
    return portfolio_return >= objective


def main():
    validate_inputs(SLEEVES, CORRELATIONS, OBJECTIVE_RETURN)
    covariance = covariance_matrix(SLEEVES, CORRELATIONS)
    names = list(SLEEVES)
    portfolios = {
        "Benchmark": benchmark_weights(SLEEVES),
        "Equal weight": equal_weights(SLEEVES),
        "Inverse volatility": inverse_volatility_weights(SLEEVES),
    }
    print(f"Objective: {OBJECTIVE_RETURN:.2%} expected annual return (CPI estimate 2.5% + 4%)")
    print("Weights order: " + " / ".join(names))
    for label, weights in portfolios.items():
        validate_weights(weights, SLEEVES)
        portfolio_return = expected_return(weights, SLEEVES)
        volatility = portfolio_volatility(weights, covariance, names)
        displayed_weights = " / ".join(f"{weights[name] * 100:.1f}" for name in names)
        print(f"{label}: weights {displayed_weights}% | return {portfolio_return:.2%} | "
              f"volatility {volatility:.2%} | reserve-eligible {reserve_eligible_weight(weights):.1%} | "
              f"meets objective: {'yes' if meets_objective(portfolio_return, OBJECTIVE_RETURN) else 'no'}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as error:
        raise SystemExit(f"Input error: {error}")
