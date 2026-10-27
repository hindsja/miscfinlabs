"""Lab 16: keep only index values knowable on a chosen decision date."""

from collections import namedtuple
from datetime import date, timedelta


# Editable inputs. Each row number identifies the corresponding course training row.
DECISION_DATE = "2026-03-31"
Row = namedtuple("Row", "number ticker month published index")
ROWS = [
    Row(1, "AAA", "2026-01", "2026-02-10", 101.0),
    Row(2, "AAA", "2026-02", "2026-03-10", 104.0),
    Row(3, "AAA", "2026-03", "2026-04-10", 109.0),
    Row(4, "AAA", "2026-02", "2026-03-25", 103.0),
    Row(5, "BBB", "2026-01", "2026-02-10", 98.0),
    Row(6, "BBB", "2026-02", "2026-03-10", 97.0),
    Row(7, "BBB", "2026-02", "2026-03-10", 97.0),
    Row(8, "BBB", "2026-03", "2026-04-10", 92.0),
    Row(9, "CCC", "2026-01", "2026-02-10", 110.0),
    Row(10, "CCC", "2026-02", "2026-04-05", 112.0),
    Row(11, "", "2026-02", "2026-03-10", 99.0),
    Row(12, "CCC", "2026-02", "2026-03-10", 111.0),
]


def latest_publications(rows):
    """Keep the newest published value for each ticker and measured month."""
    chosen = {}
    replaced = []
    for row in rows:
        key = (row.ticker, row.month)
        prior = chosen.get(key)
        if prior is None:
            chosen[key] = row
        elif row.published > prior.published:
            replaced.append(prior)
            chosen[key] = row
        elif row.published < prior.published:
            replaced.append(row)
        else:
            raise ValueError(f"Conflicting publications on the same date: rows {prior.number}, {row.number}")
    return sorted(chosen.values(), key=lambda row: (row.ticker, row.month)), replaced


def signal(rows, ticker):
    """Return (percent change, latest month, latest row) for consecutive months."""
    by_month = {row.month: row for row in rows if row.ticker == ticker}
    if not by_month:
        return None
    latest_month = max(by_month)
    previous_month = (date.fromisoformat(latest_month + "-01") - timedelta(days=1)).strftime("%Y-%m")
    if previous_month not in by_month:
        return None
    latest = by_month[latest_month]
    previous = by_month[previous_month]
    return (latest.index / previous.index - 1) * 100, latest_month, latest


def show_removal(label, rows):
    numbers = ", ".join(str(row.number) for row in sorted(rows, key=lambda row: row.number)) or "none"
    print(f"{label}: {len(rows)} removed; rows {numbers}")


def main(decision_date=DECISION_DATE):
    cutoff = date.fromisoformat(decision_date)
    if len({row.number for row in ROWS}) != len(ROWS):
        raise ValueError("Row numbers must be unique")
    for row in ROWS:
        date.fromisoformat(row.month + "-01")
        date.fromisoformat(row.published)
        if row.index <= 0:
            raise ValueError(f"Index must be positive in row {row.number}")

    # Rule 1: unknown ticker cannot be assigned to a series.
    quarantined = [row for row in ROWS if not row.ticker.strip()]
    identified = [row for row in ROWS if row.ticker.strip()]

    # Rule 2: row number is an identifier, not part of the economic observation.
    seen = set()
    unique = []
    duplicates = []
    for row in identified:
        observation = (row.ticker, row.month, row.published, row.index)
        if observation in seen:
            duplicates.append(row)
        else:
            seen.add(observation)
            unique.append(row)

    # Rule 3: a later publication was unavailable at the decision date.
    late = [row for row in unique if date.fromisoformat(row.published) > cutoff]
    knowable = [row for row in unique if date.fromisoformat(row.published) <= cutoff]

    # Rule 4: among knowable publications for a ticker/month, take the newest.
    asof_panel, replaced = latest_publications(knowable)

    print(f"Decision date: {decision_date}")
    print("Row funnel")
    show_removal("1. Quarantined: no ticker", quarantined)
    show_removal("2. Exact duplicates", duplicates)
    show_removal("3. Published after decision date", late)
    show_removal("4. Older vintages replaced", replaced)
    print("As-of panel")
    print("Row  Ticker  Month     Published   Index")
    for row in asof_panel:
        print(f"{row.number:>3}  {row.ticker:<6}  {row.month}  {row.published}  {row.index:>5.1f}")

    # Naive panel uses the same valid, deduplicated observations, but no cutoff.
    naive_panel, _ = latest_publications(unique)
    print("Signals (latest measured month versus its previous month)")
    for ticker in sorted({row.ticker for row in unique}):
        asof_result = signal(asof_panel, ticker)
        naive_result = signal(naive_panel, ticker)
        for label, result in (("As-of", asof_result), ("Naive", naive_result)):
            if result is None:
                print(f"{ticker} {label}: unavailable (consecutive months needed)")
                continue
            change, month, latest = result
            month_name = date.fromisoformat(month + "-01").strftime("%B")
            # Identify a post-decision revision of the naive latest month.
            revised_later = (
                label == "Naive"
                and date.fromisoformat(latest.published) > cutoff
                and any(
                    row.ticker == ticker and row.month == month and row.published < latest.published
                    for row in unique
                )
            )
            suffix = ", revised" if revised_later else ""
            print(f"{ticker} {label}: {change:+.2f}% ({month_name}{suffix})")


if __name__ == "__main__":
    main()
