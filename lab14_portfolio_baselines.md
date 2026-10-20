# Lab 14 — Portfolio Baselines

## Decision and inputs

The Meridian Foundation training case asks what three simple portfolios earn and
risk, and whether any meets its mandate. The four sleeve returns, volatilities,
and correlations in `portfolio.py` are course-authored **training values**, not
market estimates. CPI of 2.5% is a labelled estimate, making the comparison
objective CPI + 4% = **6.5%**. The actual mandate calls for that return annually,
net of costs, over rolling five-year periods; a one-period expected return is
only an initial screen.

Source: [FIN 43900 Lab 14](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-09/lab-14-portfolio-baselines.md),
[Week 9 handout](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-09/student-handout.md),
and the prior `lab13_mandate.md` / `mandate.py` Meridian rules.

## Baselines calculated from the inputs

All returns and volatilities below are annual percentages. Reserve-eligible
weight is bills plus the 10-year Treasury note. Weights are listed as bills /
10-year note / investment-grade bonds / global equity.

| Portfolio | Weights (%) | Expected return | Volatility | Reserve-eligible | Meets 6.5% expected-return screen? |
|---|---|---:|---:|---:|---|
| Benchmark | 0.0 / 0.0 / 40.0 / 60.0 | 6.80% | 10.46% | 0.0% | Yes |
| Equal weight | 25.0 / 25.0 / 25.0 / 25.0 | 5.20% | 5.21% | 50.0% | No |
| Inverse volatility | 84.3 / 6.0 / 7.0 / 2.6 | 3.77% | 1.05% | 90.3% | No |

**Mandate reading:** No baseline passes both the expected-return screen and the
checkable reserve rule. The benchmark clears 6.5% on the course inputs but
candidate E in `mandate.py` has 0.0% reserve weight against a 3.0% minimum.
Equal weight and inverse volatility satisfy that reserve minimum but fall short
of 6.5% expected return. This is not proof that any future return or loss limit
will be met. Costs, uncertain forecasts, and the rolling five-year horizon are
outside this simple calculation.

## Diversification and the benchmark by hand

Diversification combines exposures whose returns do not move perfectly
together. Portfolio variance includes each sleeve's own variance plus
cross-sleeve covariance. With correlation below +1, the cross terms are smaller
than they would be under perfect co-movement; common market risk still remains.

For the benchmark, bond/equity covariance is
`0.25 × 0.06 × 0.16 = 0.0024`. The portfolio variance is
`0.40² × 0.06² + 0.60² × 0.16² + 2 × 0.40 × 0.60 × 0.0024`
`= 0.000576 + 0.009216 + 0.001152 = 0.010944`.
Its annual volatility is `√0.010944 = 10.46%`. Omitting covariance would
incorrectly produce 9.90%. These calculations follow the course handout's
digits.

Inverse volatility gives the least volatile sleeve, bills, the largest weight:
its reciprocal volatility is `1 / 0.005 = 200`, far larger than the reciprocal
volatilities of the other sleeves. After scaling all reciprocals to sum to one,
bills receive 84.3%. The method does not use expected return or Meridian's
return objective, so its low-risk allocation misses the 6.5% screen.

**AI-assisted analytical choice for a CIO discussion:** Start with the client's
own 40/60 benchmark. It meets the simplified return screen while violating the
reserve rule, making the mandate conflict concrete. This is a discussion order,
not an investment recommendation or a record of a partner conversation.

## Validation and limits

`python portfolio.py` produced all three published known-answer rows. In a
temporary in-memory probe, raising both IG bond–equity correlations from 0.25
to 0.50 raised benchmark volatility to 11.00%. Changing both to 1.3 caused a
`ValueError` for a correlation outside −1 to 1; changing one cell only caused
a `ValueError` for asymmetry. The saved file retains the original 0.25 values.
`python mandate.py` produced candidate E's 0.0% reserve weight and a failed
reserve check. These executions were AI-assisted checks on 2026-10-19.

The correlations and expected returns are fixed course inputs. They are not
estimated from five years of prices, and a historical relationship could change
under stress. The engine calculates annual portfolio standard deviation from a
covariance matrix; it does not model drawdowns, transaction costs, rebalancing,
or the policy's unspecified calendar-year loss rule.
