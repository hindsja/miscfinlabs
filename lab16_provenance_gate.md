# Lab 16 — Provenance gate

The training data are a **fictional card-spend index** from the [course's Lab 16 table](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-10/lab-16-provenance-gate.md). The decision date is **2026-03-31**. `asof.py` uses only the Python standard library and computes the results from the table and date at the top of the file.

## Point-in-time result

| Rule, applied in order | Removed row numbers |
|---|---|
| Quarantine missing ticker | 11 |
| Remove exact duplicate | 7 |
| Exclude publication after decision date | 3, 8, 10 |
| Keep latest knowable publication for each ticker and month | 2 |

The remaining panel is rows **1, 4, 5, 6, 9, 12**. In particular, row 4 replaces AAA's earlier February value in row 2; its 2026-03-25 publication was available by the decision date.

| Ticker | As-of signal | Naive signal |
|---|---:|---:|
| AAA | +1.98% (February) | +5.83% (March) |
| BBB | −1.02% (February) | −5.15% (March) |
| CCC | +0.91% (February) | +1.82% (February, revised) |

The signal is `(latest month's index / previous month's index − 1) × 100`. For AAA as of March 31, it is `(103 / 101 − 1) × 100 = 1.98%`. The naive March signal uses 109, a value published on April 10, and therefore leaks future information into a March 31 decision. CCC's naive signal uses a later publication of the *same measured month*, illustrating revision leakage. A backtest using the naive column could attribute knowledge of those later values to a trader who did not have them yet. These index changes are illustrative signals, not measured trading returns or evidence of predictive performance.

## Verification

Running `python asof.py` reproduced every row and rounded signal in the course's known answer. Running `python -c "import asof; asof.main('2026-04-15')"` produced as-of signals of +5.83%, −5.15%, and +1.82%, respectively, equal to the naive signals for all three tickers. Both commands exited successfully on 2026-10-27 with Python 3.12.13. This verifies the training table only; the partner swap and explanation are separate class activities.

The code and this analysis were AI-assisted. The course training table and known answer are course-provided; the computation and verification described above were performed in this workspace.
