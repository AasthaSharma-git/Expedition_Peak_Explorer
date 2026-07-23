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
st.write("Explore India's popular 6000 m expedition peaks, compare technical grades, estimate costs, and find beginner-friendly objectives.")
    
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

tab1, tab2, tab3 = st.tabs([
    "Peak Explorer",
    "Readiness",
    "Cost Estimator"
])

with tab1:
    render_search_filter(df)
with tab2:
    render_readiness_check(df)
with tab3:
    render_cost_estimate(df)

render_closed_peak_notice()

