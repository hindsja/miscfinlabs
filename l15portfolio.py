"""Lab 15 search and CSV estimates extending the Lab 14 Meridian engine.

Run: python l15portfolio.py
Returns and volatilities are annual decimal fractions (0.035 means 3.5%).
"""

import csv
import math
import statistics
from datetime import date
from pathlib import Path


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


def lowest_risk_mix(sleeves, correlations, objective, reserve_eligible=(), reserve_minimum=0.0):
    """Search every long-only 5-point mix; return the feasible lowest-risk result."""
    validate_inputs(sleeves, correlations, objective)
    if not math.isfinite(reserve_minimum) or not 0 <= reserve_minimum <= 1:
        raise ValueError("Reserve minimum must be between 0% and 100%.")
    names = list(sleeves)
    eligible = set(reserve_eligible)
    if not eligible.issubset(sleeves):
        raise ValueError("Reserve-eligible assets must be in the universe.")
    covariance = covariance_matrix(sleeves, correlations)
    best = None

    def try_mixes(units_left, units):
        nonlocal best
        if len(units) == len(names) - 1:
            candidate_units = units + [units_left]
            weights = {name: units / 20 for name, units in zip(names, candidate_units)}
            portfolio_return = expected_return(weights, sleeves)
            reserve_weight = math.fsum(weights[name] for name in eligible)
            if portfolio_return + 1e-12 < objective or reserve_weight + 1e-12 < reserve_minimum:
                return
            volatility = portfolio_volatility(weights, covariance, names)
            if best is None or volatility < best["volatility"] - 1e-12:
                best = {"weights": weights, "return": portfolio_return,
                        "volatility": volatility, "reserve_weight": reserve_weight}
            return
        for units_here in range(units_left + 1):
            try_mixes(units_left - units_here, units + [units_here])

    try_mixes(20, [])
    return best


def estimate_from_prices(csv_file, last_36_months=False):
    """Estimate annual return/volatility and correlation from monthly Adj Close CSV."""
    if hasattr(csv_file, "read"):
        csv_file.seek(0)
        content = csv_file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8-sig")
    else:
        content = Path(csv_file).read_text(encoding="utf-8-sig")
    rows = csv.DictReader(content.splitlines())
    headers, records = rows.fieldnames, list(rows)
    if not headers or len(headers) < 4 or headers[0].strip().lower() != "date":
        raise ValueError("CSV needs date first and at least three ticker columns.")
    names = [name.strip() for name in headers[1:]]
    if len(names) > 6 or any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError("CSV needs three to six unique, named ticker columns.")
    if len(records) < (37 if last_36_months else 3):
        raise ValueError("Not enough monthly prices for the selected estimation window.")
    dates = []
    prices = {name: [] for name in names}
    months = set()
    for row in records:
        try:
            day = date.fromisoformat(row[headers[0]].strip())
        except (ValueError, AttributeError, TypeError) as error:
            raise ValueError("Dates must use YYYY-MM-DD and have no blanks.") from error
        month = (day.year, day.month)
        if month in months or (dates and day <= dates[-1]):
            raise ValueError("Price dates must be unique months, oldest first.")
        months.add(month)
        dates.append(day)
        for original, name in zip(headers[1:], names):
            try:
                value = float(row[original])
            except (ValueError, TypeError) as error:
                raise ValueError(f"Missing or invalid price for {name} on {day}.") from error
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"Price for {name} on {day} must be positive and finite.")
            prices[name].append(value)
    returns = {name: [new / old - 1 for old, new in zip(values, values[1:])]
               for name, values in prices.items()}
    if last_36_months:
        returns = {name: values[-36:] for name, values in returns.items()}
    count = len(next(iter(returns.values())))
    if count < 2:
        raise ValueError("At least two monthly returns are required.")
    means = {name: statistics.mean(values) for name, values in returns.items()}
    monthly_vols = {name: statistics.stdev(values) for name, values in returns.items()}
    if any(vol <= 0 for vol in monthly_vols.values()):
        raise ValueError("A ticker has zero monthly volatility; correlation is undefined.")
    sleeves = {name: {"return": means[name] * 12,
                      "volatility": monthly_vols[name] * math.sqrt(12)} for name in names}
    correlations = [
        [1.0 if i == j else statistics.correlation(returns[left], returns[right])
         for j, right in enumerate(names)]
        for i, left in enumerate(names)
    ]
    validate_inputs(sleeves, correlations, 0.0)
    return sleeves, correlations, dates[-count - 1], dates[-1], count


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
