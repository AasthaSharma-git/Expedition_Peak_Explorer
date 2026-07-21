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

df = load_data()

st.title("Expedition Peak Explorer")

def render_search_filter(df: pd.DataFrame) -> None:
    """Render region/grade/IMF filters and display peak table."""
    region_filter = st.multiselect("Region", options = sorted(df["region"].unique()))
    grade_filter = st.multiselect("Technical Grade", options = sorted(df["technical_grade"].unique()))
    imf_only = st.checkbox("IMF-listed peaks only")

    filtered = df.copy()

    if region_filter:
        filtered = filtered[filtered["region"].isin(region_filter)]
    if grade_filter:
        filtered = filtered[filtered["technical_grade"].isin(grade_filter)]
    if imf_only:
        filtered = filtered[filtered["imf_listed"]==True]

    st.dataframe(filtered[["name","region","altitude_m","technical_grade","typical_duration_days"]])

def render_readiness_check(df: pd.DataFrame) -> None:
    """Render peak readiness"""
    st.header("First 6000er Readiness Check")

    experience_level = st.radio(
            "Have you completed a BMC (Basic Mountaineering Course)",
            ["Yes", "No"]
    )

    if experience_level == "Yes":
        recommended = df[df["bmc_recommended_first_peak"] == True]
        st.write(f"{len(recommended)} peaks recommended for a first-time BMC graduate: ")
        st.dataframe(recommended[["name","region","altitude_m","technical_grade","typical_duration_days","nights_above_5000m"]])
    else:
        st.warning("Complete a BMC course before attempting any of these peaks.")

def render_cost_estimate(df: pd.DataFrame) -> None:
    """Render expedition cost estimate"""
    st.header("Expedition Cost Estimate")

    peak_choice = st.selectbox("Select a peak", options=df["name"].sort_values())
    peak_row = df[df["name"] == peak_choice].iloc[0]

    st.subheader(peak_choice)

    basecamp = peak_row["basecamp_m"]
    summit = peak_row["altitude_m"]

    low, high = peak_row["operator_cost_inr_band"]
    st.write(f"**Operator fee:** ₹{low:,} -  ₹{high:,}")
    st.write(f"**Base camp:** {basecamp:,}m → **Summit:** {summit:,}m")

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

render_search_filter(df)
render_readiness_check(df)
render_cost_estimate(df)
render_closed_peak_notice()

