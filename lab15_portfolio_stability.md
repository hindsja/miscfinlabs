# Lab 15 — Portfolio Stability Decision

## Decision and mandate used

The intended user is a portfolio analyst considering a starting allocation among
four exchange-traded funds selected for this exercise. The search minimizes
annualized historical volatility among long-only mixes in 5-percentage-point
steps that meet an expected-return screen. **AI-assisted working assumptions:**
6.5% expected annual return objective and **no reserve constraint (0%)** because
this four-fund universe contains no reserve fund. These are provisional lab
inputs, not a confirmed Project 2 investment policy. The app cannot establish a
future 6.5% return or check the other Meridian policy rules.

| Fund | Role in this exercise | Provider description |
|---|---|---|
| EWY | South Korean equity exposure | [iShares MSCI South Korea ETF](https://www.ishares.com/us/products/239681/ishares-msci-south-korea-etf) |
| QQQM | U.S. large growth exposure | [Invesco NASDAQ 100 ETF](https://www.invesco.com/us/en/financial-products/etfs/invesco-nasdaq-100-etf.html) |
| VOO | Broad U.S. large-cap benchmark exposure | [Vanguard S&P 500 ETF](https://advisors.vanguard.com/investments/products/voo/vanguard-sp-500-etf) |
| FNDX | Fundamentally weighted U.S. large-company exposure | [Schwab Fundamental U.S. Large Company ETF](https://www.schwabassetmanagement.com/products/fndx) |

## Prices and sources

`prices.csv` contains **61 monthly Adj Close prices** for each ticker from
September 2021 through September 2026, in U.S. dollars, oldest month first.
Each `Date` is the first day *labeling the monthly Yahoo bar*; its price is that
month's adjusted close, not the daily closing price on the labeled date. The
file was downloaded and built on **2026-10-21** with `build_prices.py`. The
script requests Yahoo Finance's monthly chart `adjclose` series and checks for
matching months, positive prices, and USD currency. Exact source endpoints:

| Ticker | Monthly Adj Close source | Download date |
|---|---|---|
| EWY | [Yahoo Finance monthly chart](https://query2.finance.yahoo.com/v8/finance/chart/EWY?period1=1630454400&period2=1790812800&interval=1mo&events=history&includeAdjustedClose=true) | 2026-10-21 |
| QQQM | [Yahoo Finance monthly chart](https://query2.finance.yahoo.com/v8/finance/chart/QQQM?period1=1630454400&period2=1790812800&interval=1mo&events=history&includeAdjustedClose=true) | 2026-10-21 |
| VOO | [Yahoo Finance monthly chart](https://query2.finance.yahoo.com/v8/finance/chart/VOO?period1=1630454400&period2=1790812800&interval=1mo&events=history&includeAdjustedClose=true) | 2026-10-21 |
| FNDX | [Yahoo Finance monthly chart](https://query2.finance.yahoo.com/v8/finance/chart/FNDX?period1=1630454400&period2=1790812800&interval=1mo&events=history&includeAdjustedClose=true) | 2026-10-21 |

These are historical **estimates**, not forecasts. Monthly simple return is
`new adjusted price / prior adjusted price − 1`; annual return estimate is its
mean × 12; annual volatility estimate is its sample standard deviation × √12.
Correlations use the same monthly returns. The 36-month view uses the last 36
returns, not the last 36 price rows. No missing price was filled. Adjusted
historical prices may be revised after corporate actions, so `prices.csv` is the
point-in-time downloaded copy used for the results below.

| Annual estimate | EWY | QQQM | VOO | FNDX |
|---|---:|---:|---:|---:|
| Return, all 60 monthly returns | 25.45% | 17.42% | 14.18% | 14.21% |
| Volatility, all 60 | 38.12% | 20.87% | 15.67% | 14.98% |
| Return, last 36 monthly returns | 49.18% | 26.45% | 21.49% | 19.99% |
| Volatility, last 36 | 42.57% | 17.25% | 12.45% | 11.68% |

## Meridian known-answer and engine checks

The Lab 14 `portfolio.py` is kept as the original version. The Lab 15
`l15portfolio.py` preserves its printout and adds the search and CSV estimator;
`app.py` imports the new module's engine and Meridian inputs. Executed checks on **2026-10-21** matched the
course's published answers:

| Input | Bills / 10-year / IG / equity | Return | Volatility |
|---|---|---:|---:|
| As loaded | 0 / 20 / 25 / 55 | 6.51% | 9.44% |
| Equity return 8% → 7% | 0 / 10 / 10 / 80 | 6.53% | 12.94% |
| IG–equity correlation 0.25 → 0.50 in both cells | 0 / 40 / 0 / 60 | 6.52% | 9.73% |

The equity-return stress changes the largest weight by **25 percentage points**.
For the correlation check, both cells were temporarily changed in
`l15portfolio.py`; the app showed the expected 0 / 40 / 0 / 60 mix, and both cells
were restored to 0.25. Streamlit's app test showed no exceptions for the
loaded and edited Meridian pages. The running app passed a local HTTP health
check. A separate pandas calculation matched the CSV return estimates and both
reported portfolio return/volatility pairs.

## Four-fund results and stability

The order below is EWY / QQQM / VOO / FNDX. Both searches use the provisional
6.5% objective and 0% reserve minimum. The return estimates differ by window;
each mix is chosen from the 5-point grid using the corresponding window's
volatilities and correlations.

| Estimation window | Lowest-risk feasible weights | Return estimate | Volatility estimate | Reserve weight |
|---|---|---:|---:|---:|
| All 60 monthly returns, Sep 2021–Sep 2026 | 0 / 0 / 25 / 75 | 14.20% | 14.91% | 0% |
| Last 36 monthly returns, Sep 2023–Sep 2026 | 0 / 0 / 25 / 75 | 20.36% | 11.57% | 0% |

**Largest weight change: 0 percentage points.** The allocation holds under
this window switch, but its estimated return increases 6.16 points and its
estimated volatility falls 3.34 points. Thus an unchanged weight is not proof
of a stable forecast. Because the 6.5% screen sits below every fund's estimated
return in both windows, it does little to constrain the minimum-volatility
search. The result favors the lower-volatility, highly overlapping U.S. equity
funds; the four-fund universe supplies no defensive reserve sleeve. Correlation
and volatility estimated from one historical regime can change.

**AI-assisted provisional call: pilot for analysis, not adoption as a Project 2
allocation.** The 25% VOO / 75% FNDX mix survives the 36-month weight test, but
its volatility estimate changes materially. Adoption would require a defined
investor objective and hard constraints, a reserve solution if the mandate needs
one, and further cost and out-of-sample checks that support the risk estimate.
The current screen uses historical gross returns; it does not account for
trading costs, rebalancing, tax, drawdowns, or a future loss limit.

Sources for the lab method and Meridian answers: [FIN 43900 Lab 15](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-09/lab-15-portfolio-stability.md)
and [Lab 14](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-09/lab-14-portfolio-baselines.md).
