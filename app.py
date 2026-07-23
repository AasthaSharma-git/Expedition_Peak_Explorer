import streamlit as st
import pandas as pd
import json

@st.cache_data
def load_data():
    """Load peak data from local JSON cache. Stops the app with a clear message if missing."""
    try:
        with open("data/raw_peaks.json", encoding="utf-8") as f:
            raw = json.load(f)
        return pd.DataFrame(raw["data"])
    except FileNotFoundError:
        st.error("data/raw_peaks.json not found. Run fetch_data.py first.")
        st.stop()

def render_search_filter(df: pd.DataFrame) -> None:
    """Render region/grade/IMF filters and display peak table."""
    region_filter = st.pills("Region", options = sorted(df["region"].unique()), selection_mode="multi")
    grade_filter = st.pills("Technical Grade", options = sorted(df["technical_grade"].unique()), selection_mode="multi")

    grade_help = {
    "F": "Easy glacier walking and straightforward terrain.",
    "PD": "Moderate snow and rock. Ice axe, crampons, and rope work required.",
    "PD+": "More sustained than PD with a few technical sections.",
    "AD-": "Beginning of serious alpine climbing with continuous exposure.",
    "AD": "Steep snow, ice, or rock requiring solid technical skills.",
    "AD+": "Harder crux or longer sustained technical climbing.",
    "D": "Physically demanding climbing with advanced rope work.",
    "D+": "Very sustained and technically challenging alpine climbing.",
    "TD": "Expert-level routes with significant exposure and objective hazards."
    }

    with st.expander("ℹ️ Technical Grade Guide"):
        for grade in sorted(df["technical_grade"].unique()):
            if grade in grade_help:
                st.markdown(f"**{grade}** : {grade_help[grade]}")

    imf_only = st.checkbox("IMF-listed peaks only")

    col1, col2, col3 = st.columns(3)
  
    filtered = df.copy()

    col1.metric("Peaks", len(filtered))
    col2.metric("Highest Peak", f"{filtered['altitude_m'].max():,.0f} m")
    col3.metric("IMF Peaks", filtered["imf_listed"].sum())

    if region_filter:
        filtered = filtered[filtered["region"].isin(region_filter)]
    if grade_filter:
        filtered = filtered[filtered["technical_grade"].isin(grade_filter)]
    if imf_only:
        filtered = filtered[filtered["imf_listed"]==True]

    st.dataframe(filtered[["name","region","altitude_m","technical_grade","typical_duration_days"]])

def render_peak_comparison(df: pd.DataFrame) -> None:
    """Compare two expedition peaks side by side."""

    st.header("Peak Comparison")

    col1, col2 = st.columns(2)

    with col1:
        peak1_name = st.selectbox(
            "Peak A",
            sorted(df["name"].unique()),
            key="peak_a",
        )

    with col2:
        peak2_name = st.selectbox(
            "Peak B",
            sorted(df["name"].unique()),
            index=1,
            key="peak_b",
        )

    if peak1_name == peak2_name:
        st.info("Please select two different peaks.")
        return

    peak1 = df.loc[df["name"] == peak1_name].iloc[0]
    peak2 = df.loc[df["name"] == peak2_name].iloc[0]

    grade_order = {
        "F": 1,
        "F+": 2,
        "PD": 3,
        "PD+": 4,
        "AD-": 5,
        "AD": 6,
        "AD+": 7,
        "D": 8,
        "D+": 9,
        "TD": 10,
    }

    st.subheader("Quick Overview")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"### {peak1['name']}")
        st.metric("Altitude", f"{peak1['altitude_m']} m")
        st.metric("Technical Grade", peak1["technical_grade"])
        st.metric("Duration", f"{peak1['typical_duration_days']} Days")
        st.metric(
            "Operator Cost",
            f"₹{peak1['operator_cost_inr_band'][0]:,} - ₹{peak1['operator_cost_inr_band'][1]:,}",
        )

    with c2:
        st.markdown(f"### {peak2['name']}")
        st.metric("Altitude", f"{peak2['altitude_m']} m")
        st.metric("Technical Grade", peak2["technical_grade"])
        st.metric("Duration", f"{peak2['typical_duration_days']} Days")
        st.metric(
            "Operator Cost",
            f"₹{peak2['operator_cost_inr_band'][0]:,} - ₹{peak2['operator_cost_inr_band'][1]:,}",
        )

    st.divider()

    st.subheader("Detailed Comparison")

    comparison = pd.DataFrame(
        {
            peak1["name"]: [
                peak1["region"],
                peak1["basecamp_name"],
                f"{peak1['basecamp_m']} m",
                peak1["roadhead"],
                "Yes" if peak1["imf_listed"] else "No",
                "Yes" if peak1["inner_line_permit_required"] else "No",
                ", ".join(peak1["best_months"]),
            ],
            peak2["name"]: [
                peak2["region"],
                peak2["basecamp_name"],
                f"{peak2['basecamp_m']} m",
                peak2["roadhead"],
                "Yes" if peak2["imf_listed"] else "No",
                "Yes" if peak2["inner_line_permit_required"] else "No",
                ", ".join(peak2["best_months"]),
            ],
        },
        index=[
            "Region",
            "Base Camp",
            "Base Camp Altitude",
            "Roadhead",
            "IMF Listed",
            "Permit Required",
            "Best Season",
        ],
    )

    st.table(comparison)

    st.divider()

    st.subheader("Skills Required")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {peak1['name']}")
        for skill in peak1["key_skills"]:
            st.write(f"{skill}")

    with col2:
        st.markdown(f"#### {peak2['name']}")
        for skill in peak2["key_skills"]:
            st.write(f"{skill}")

    st.divider()

    st.subheader("Quick Verdict")

    verdict = []

    easier = (
        peak1["name"]
        if grade_order[peak1["technical_grade"]]
        < grade_order[peak2["technical_grade"]]
        else peak2["name"]
    )

    cheaper = (
        peak1["name"]
        if peak1["operator_cost_inr_band"][1]
        < peak2["operator_cost_inr_band"][1]
        else peak2["name"]
    )

    shorter = (
        peak1["name"]
        if peak1["typical_duration_days"]
        < peak2["typical_duration_days"]
        else peak2["name"]
    )

    higher = (
        peak1["name"]
        if peak1["altitude_m"] > peak2["altitude_m"]
        else peak2["name"]
    )

    verdict.append(("Easier Climb", easier))
    verdict.append(("Cheaper Expedition", cheaper))
    verdict.append(("Shorter Expedition", shorter))
    verdict.append(("Higher Peak", higher))

    verdict_df = pd.DataFrame(verdict, columns=["Category", "Winner"])
    st.table(verdict_df)

def render_cost_estimate(df: pd.DataFrame) -> None:
    """Render expedition cost estimate"""
    st.header("Expedition Cost Estimate")

    peak_choice = st.selectbox("Select a peak", options=df["name"].sort_values())
    peak_row = df[df["name"] == peak_choice].iloc[0]

    st.subheader(peak_choice)
    
    basecamp = peak_row["basecamp_m"]
    summit = peak_row["altitude_m"]

    low, high = peak_row["operator_cost_inr_band"]
    
    left, right = st.columns(2)

    with left:
        st.metric(f"**Altitude:**", f"{summit:,} m")
        st.metric(f"**Base camp:**", f"{basecamp:,} m")
    with right:
        st.metric(f"**Operator fee:**", f"₹{low:,} -  ₹{high:,}")
   

    if peak_row["imf_listed"]:
        st.write(f"**IMF royalty (party of 2):** ${peak_row['imf_royalty_usd_party_of_2']:,.0f}")
    else: 
        st.write("**IMF royalty:** Not applicable - climbed as a trekking peak, not IMF-listed.")

    if peak_row["inner_line_permit_required"]:
        st.warning("Inner Line Permit / Protected Area Permit required for this region.")
    else:
        st.write("**Permits:** No special permit required beyond standard ID.")

    st.caption("Estimate excludes gear, travel to roadhead, and personal expenses. Verify IMF fees directly with IMF at booking time")

def render_closed_peak_notice() -> None:
    """Static advisory — not pulled from the API response, which only returns the peak list."""
    st.info(
        "⚠️ **Stok Kangri has been closed since 2020** for ecological recovery "
        "(per The Vertical Tribe's peak dataset documentation). Open alternatives "
        "in this list: UT Kangri, Kang Yatse II, Dzo Jongo East, Mentok Kangri II."
    )

df = load_data()

st.title("Expedition Peak Explorer")
st.write("Explore India's popular 6000 m expedition peaks, compare technical grades, estimate costs, and find beginner-friendly objectives.")

render_closed_peak_notice()    

tab1, tab2, tab3 = st.tabs([
    "Peak Explorer",
    "Peak Comparision",
    "Cost Estimator"
])

with tab1:
    render_search_filter(df)
with tab2:
    render_peak_comparison(df)
with tab3:
    render_cost_estimate(df)



