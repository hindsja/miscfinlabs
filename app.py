"""Lab 15 portfolio stability page. Run: python -m streamlit run app.py"""

import streamlit as st

from l15portfolio import (
    CORRELATIONS,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    SLEEVES,
    estimate_from_prices,
    lowest_risk_mix,
)


def show_result(result, names):
    if result is None:
        st.warning("no mix meets the objective")
        return
    for name in names:
        st.write(f"{name}: **{result['weights'][name]:.0%}**")
    st.write(f"Expected return: **{result['return']:.2%}**")
    st.write(f"Volatility: **{result['volatility']:.2%}**")
    st.write(f"Reserve-eligible weight: **{result['reserve_weight']:.2%}**")


st.set_page_config(page_title="Portfolio Stability Decision", layout="wide")
st.title("Portfolio Stability Decision")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    st.header("Mandate and data")
    objective_percent = st.number_input(
        "Objective: expected annual return (%)", value=OBJECTIVE_RETURN * 100,
        step=0.1, format="%.2f",
    )
    reserve_percent = st.number_input(
        "Minimum reserve-eligible weight (%)", min_value=0.0, max_value=100.0,
        value=3.0, step=1.0, format="%.2f",
    )
    uploaded = st.file_uploader("Upload monthly Adj Close prices.csv", type="csv")
    last_36 = st.checkbox("Use only last 36 monthly returns")

if uploaded is None:
    st.subheader("Meridian training inputs")
    loaded_sleeves = {name: values.copy() for name, values in SLEEVES.items()}
    current_sleeves = {name: values.copy() for name, values in SLEEVES.items()}
    correlations = CORRELATIONS
    loaded_correlations = CORRELATIONS
    default_eligible = set(RESERVE_ELIGIBLE)
    if last_36:
        st.info("The 36-month switch applies to an uploaded CSV; Meridian uses fixed course inputs.")
    source_key = "meridian"
else:
    st.subheader("Uploaded fund universe")
    try:
        loaded_sleeves, loaded_correlations, full_start, full_end, full_count = (
            estimate_from_prices(uploaded)
        )
        current_sleeves, correlations, start, end, count = (
            estimate_from_prices(uploaded, last_36_months=last_36)
        )
    except (ValueError, UnicodeDecodeError) as error:
        st.error(f"Price CSV error: {error}")
        st.stop()
    st.caption(
        f"Annual return estimates from {count} monthly returns ({start} to {end}). "
        f"As loaded uses all {full_count} returns ({full_start} to {full_end}). "
        "History is not a forecast."
    )
    default_eligible = set()
    source_key = uploaded.name

names = list(current_sleeves)
st.write("Edit the expected annual return estimates and select the funds that count toward the reserve.")
eligible = []
for index, name in enumerate(names):
    left, right = st.columns([2, 1])
    with left:
        edited_percent = st.number_input(
            f"{name} expected annual return estimate (%)",
            value=current_sleeves[name]["return"] * 100,
            min_value=-100.0, max_value=100.0, step=0.25, format="%.2f",
            key=f"return_{source_key}_{last_36}_{index}",
        )
        current_sleeves[name]["return"] = edited_percent / 100
    with right:
        if st.checkbox(
            f"{name} reserve-eligible", value=name in default_eligible,
            key=f"eligible_{source_key}_{index}",
        ):
            eligible.append(name)

try:
    loaded_result = lowest_risk_mix(
        loaded_sleeves, loaded_correlations, objective_percent / 100,
        eligible, reserve_percent / 100,
    )
    current_result = lowest_risk_mix(
        current_sleeves, correlations, objective_percent / 100,
        eligible, reserve_percent / 100,
    )
except ValueError as error:
    st.error(f"Portfolio input error: {error}")
    st.stop()

current_col, loaded_col = st.columns(2)
with current_col:
    st.subheader("Current controls")
    show_result(current_result, names)
with loaded_col:
    st.subheader("As loaded")
    st.caption("Original expected returns; all months if a CSV is uploaded. Current objective and reserve rule apply to both answers.")
    show_result(loaded_result, names)

if loaded_result is not None and current_result is not None:
    largest_change = max(
        abs(current_result["weights"][name] - loaded_result["weights"][name]) * 100
        for name in names
    )
    st.metric("Largest weight change", f"{largest_change:.0f} percentage points")
else:
    st.write("Largest weight change: unavailable because at least one mix is infeasible.")

st.caption("Search uses long-only allocations in 5-percentage-point steps. Volatility is annualized standard deviation; costs and future returns are not modeled.")
