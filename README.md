# Expedition Peak Explorer

A Streamlit app to help first-time Himalayan climbers in India explore, filter, and plan around beginner-to-intermediate 6,000m (and reference 7,000m) expedition peaks.

## What it does

- **Search & filter** — narrow peaks by region, technical grade, and IMF-listed status.
- **First 6000er readiness check** — for climbers who've completed a Basic Mountaineering Course (BMC), surfaces peaks flagged as suitable first 6,000ers based on the dataset's own readiness criteria (technical grade ≤ PD+, open peak status, sufficient acclimatization nights, and road access).
- **Expedition cost estimate** — combines operator fee bands, IMF royalty (where applicable), and Inner Line Permit requirements into a single per-peak cost and permit summary.

## Data source

Peak data is sourced from **The Vertical Tribe's Indian Himalayan Peak Dataset (v2.0.0)**, licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

> The Vertical Tribe. *Indian Himalayan Peak Dataset*, version 2.0.0. Released 2026-04-30. https://theverticaltribe.com/peak-data/. Licensed under CC-BY-4.0.

Data is fetched once via `fetch_data.py` and cached locally as `data/raw_peaks.json` — the app does not call the live API on every run.

### Approach

Before writing any feature code, the fetched data was audited in `notebooks/data_audit.ipynb` — row counts, null distribution per column, and value counts on key categorical fields (`technical_grade`, `imf_listed`). This confirmed which columns were fully populated (safe to build features on directly) versus which had expected nulls (e.g., `imf_royalty_usd_party_of_2` is null exactly for the 5 peaks not on the IMF open-peaks list), before any UI was built on top of assumptions about the data.

### Data caveats (documented upfront, not discovered by accident)

- Several peak altitudes and coordinates are **operator-derived estimates**, not surveyed figures — the dataset itself flags disagreement between sources (e.g., Wikipedia, PeakVisor, and Indian tour operators) for peaks like Kanamo, Dzo Jongo East, and CB-13. Where this happens, the dataset's own "most-published commercial figure" is used.
- `first_ascent_year` and `first_ascent_party` are null for several peaks where no verifiable record exists.
- IMF royalty figures are per the IMF's published schedule for a party of two; per-additional-member fees are not publicly posted and should be verified directly with IMF at time of booking.
- The live API response returns only the peak list (`data`), not the dataset's full metadata block (schema, closed-peaks registry, changelog). The Stok Kangri closure notice shown in the app is therefore a static, manually-added note based on the dataset's published documentation, not a live API field.

## Tech stack

- Python
- Pandas — data loading and filtering
- Streamlit — UI and app framework

## Running locally

```bash
pip install -r requirements.txt
python fetch_data.py   # fetches and caches peak data locally (run once, or to refresh)
streamlit run app.py
```

## Project structure

```
Expedition-Peak-Explorer/
├── data/
│   └── raw_peaks.json          # cached API response
├── notebooks/
│   └── data_audit.ipynb        # one-time exploration: shape, nulls, value counts (not part of app runtime)
├── app.py                      # Streamlit app
├── fetch_data.py               # one-time data fetch script
├── requirements.txt
└── README.md
```