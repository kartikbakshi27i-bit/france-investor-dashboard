import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="France Investor Pitch Dashboard", layout="wide")
st.title("France – Investor Pitch Dashboard (Investor View)")
st.caption("Built for PGDM (MEEB): Macro Trends → Competitiveness → Sector Bets → Risks & Policy Mitigation")

# -----------------------------
# Path setup: load CSVs from SAME FOLDER as app.py
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_csv(filename: str) -> pd.DataFrame:
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        st.error(f"Missing file: {path}")
        st.write("✅ Running from:", BASE_DIR)
        st.write("✅ Files available:", os.listdir(BASE_DIR))
        st.stop()
    return pd.read_csv(path)

# -----------------------------
# Helpers
# -----------------------------
def clean_macro(df: pd.DataFrame, year_col: str, value_col: str) -> pd.DataFrame:
    df = df.copy()
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    if "Type" in df.columns:
        df["Type"] = df["Type"].astype(str).str.strip()
    df = df.dropna(subset=[year_col, value_col]).sort_values(year_col)
    return df

def plot_hist_forecast_band(df, year_col, value_col, title, y_label, band_center, band_width):
    df = clean_macro(df, year_col, value_col)

    # Handle if Type column exists (Historical vs Forecast)
    if "Type" in df.columns:
        hist = df[df["Type"].str.lower() == "historical"]
        fcst = df[df["Type"].str.lower() == "forecast"]
    else:
        hist = df
        fcst = pd.DataFrame()

    fig, ax = plt.subplots(figsize=(8.2, 4.2))

    # Expected band
    lower = band_center - band_width / 2
    upper = band_center + band_width / 2
    ax.axhspan(lower, upper, alpha=0.15, label="Expected Range")
    ax.axhline(band_center, linestyle="--", linewidth=1)

    # Historical
    if not hist.empty:
        ax.plot(hist[year_col], hist[value_col], marker="o", linewidth=2, label="Historical")

    # Forecast
    if not fcst.empty:
        ax.plot(fcst[year_col], fcst[value_col], marker="o", linewidth=2, linestyle="--", label="Forecast (to 2030)")
        if not hist.empty:
            ax.plot(
                [hist[year_col].iloc[-1], fcst[year_col].iloc[0]],
                [hist[value_col].iloc[-1], fcst[value_col].iloc[0]],
                linestyle="--", linewidth=1, alpha=0.6
            )

    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(y_label)

    years = df[year_col].astype(int).tolist()
    ax.set_xticks(years)

    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="upper right")
    return fig

# -----------------------------
# Load CSV files (from SAME folder)
# -----------------------------
# These names must match exactly what is in your folder
gdp = load_csv("france_gdp.csv")                 # Year, GDP_Growth_Percent, Type
inflation = load_csv("france_inflation.csv")     # Year, Inflation_HICP_Percent, Type
unemp = load_csv("france_unemployment.csv")      # Year, Unemployment_Rate_Percent, Type

lpi = load_csv("france_lpi.csv")                 # Year, LPI_Score
ftth = load_csv("france_ftth.csv")               # Year, FTTH_Penetration_Percent

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Dashboard Controls")
st.sidebar.subheader("Expected Range Bands (Editable for Pitch)")

gdp_center = st.sidebar.slider("GDP band center (%)", -2.0, 4.0, 0.5, 0.1)
gdp_width  = st.sidebar.slider("GDP band width (%)", 0.2, 6.0, 1.2, 0.1)

inf_center = st.sidebar.slider("Inflation band center (%)", 0.0, 10.0, 2.0, 0.1)
inf_width  = st.sidebar.slider("Inflation band width (%)", 0.2, 10.0, 2.0, 0.1)

un_center  = st.sidebar.slider("Unemployment band center (%)", 3.0, 12.0, 7.2, 0.1)
un_width   = st.sidebar.slider("Unemployment band width (%)", 0.2, 8.0, 1.5, 0.1)

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["Macro Stability", "Competitiveness", "Sector Bets (Investor Pitch)"])

# -----------------------------
# TAB 1: Macro Stability
# -----------------------------
with tab1:
    st.subheader("Macro Stability (Investor Comfort Layer)")
    st.write("Investors first ask: **Is the macro environment stable enough to deploy capital?**")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.pyplot(plot_hist_forecast_band(
            gdp, "Year", "GDP_Growth_Percent",
            "GDP Growth (Historical vs Forecast to 2030)",
            "%", gdp_center, gdp_width
        ))

    with c2:
        st.pyplot(plot_hist_forecast_band(
            inflation, "Year", "Inflation_HICP_Percent",
            "Inflation (HICP) (Historical vs Forecast to 2030)",
            "%", inf_center, inf_width
        ))

    with c3:
        st.pyplot(plot_hist_forecast_band(
            unemp, "Year", "Unemployment_Rate_Percent",
            "Unemployment Rate (Historical vs Forecast to 2030)",
            "%", un_center, un_width
        ))

    st.success("Macro takeaway: France can be positioned as stability-over-volatility (lower risk premium).")

# -----------------------------
# TAB 2: Competitiveness
# -----------------------------
with tab2:
    st.subheader("Competitiveness (Execution Capability)")
    st.write("Investors ask: **Can the country execute operations reliably?**")

    d1, d2 = st.columns(2)

    with d1:
        st.markdown("### Logistics Performance Index (World Bank)")
        lpi_clean = clean_macro(lpi, "Year", "LPI_Score")
        fig, ax = plt.subplots(figsize=(8.2, 4.2))
        ax.bar(lpi_clean["Year"].astype(int), lpi_clean["LPI_Score"])
        ax.set_title("France – LPI Trend")
        ax.set_xlabel("Year")
        ax.set_ylabel("LPI Score")
        ax.grid(True, axis="y", alpha=0.25)
        st.pyplot(fig)

    with d2:
        st.markdown("### FTTH Penetration (OECD)")
        ftth_clean = clean_macro(ftth, "Year", "FTTH_Penetration_Percent")
        fig, ax = plt.subplots(figsize=(8.2, 4.2))
        ax.plot(ftth_clean["Year"].astype(int), ftth_clean["FTTH_Penetration_Percent"], marker="o", linewidth=2)
        ax.set_title("France – FTTH Trend")
        ax.set_xlabel("Year")
        ax.set_ylabel("%")
        ax.grid(True, axis="y", alpha=0.25)
        st.pyplot(fig)

# -----------------------------
# TAB 3: Sector Bets (Investor Pitch)
# -----------------------------
with tab3:
    st.subheader("Sector Bets (Investor Pitch)")
    st.write("Macro variables influence each sector differently. This section helps you pitch where to invest in France.")

    scorecard = pd.DataFrame([
        {"Sector": "Healthcare & Life Sciences (Health 2030)", "Macro Resilience": 9, "Policy Support": 9, "Export/Scale": 7, "Overall": 8.5},
        {"Sector": "Aerospace & Défense", "Macro Resilience": 8, "Policy Support": 8, "Export/Scale": 9, "Overall": 8.5},
        {"Sector": "Luxury & High-End Tourism", "Macro Resilience": 6, "Policy Support": 7, "Export/Scale": 9, "Overall": 7.5},
        {"Sector": "Agri-Food Tech", "Macro Resilience": 8, "Policy Support": 8, "Export/Scale": 7, "Overall": 7.8},
    ]).sort_values("Overall", ascending=False)

    st.markdown("### Sector Opportunity Scorecard")
    st.dataframe(scorecard, use_container_width=True)

    st.markdown("### Pitch Cards (Macro → Opportunity → Risk → Policy Mitigation)")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("#### Healthcare & Life Sciences (Health 2030)")
        st.markdown("""
- **Macro link:** demand is stable even in slow growth; inflation affects costs; rates affect R&D capital  
- **Opportunity:** biotech, diagnostics, med-tech, digital health, ageing-care solutions  
- **Risks:** regulation, long approval cycles  
- **Policy support:** mission-driven ecosystem funding + healthcare demand anchor
""")

        st.markdown("#### Aerospace & Défense")
        st.markdown("""
- **Macro link:** export driven; long contracts; supply chain sensitive to inflation  
- **Opportunity:** avionics, dual-use tech, space systems, MRO recurring revenue  
- **Risks:** tender cycles, certification delays  
- **Policy support:** strategic autonomy & procurement demand stability
""")

    with colB:
        st.markdown("#### Luxury & High-End Tourism")
        st.markdown("""
- **Macro link:** global income cycles matter; pricing power helps inflation  
- **Opportunity:** premium experiences, hospitality, sustainable tourism, luxury retail  
- **Risks:** global shocks (travel), reputational risk  
- **Policy support:** infrastructure & destination investment; brand moat
""")

        st.markdown("#### Agri-Food Tech")
        st.markdown("""
- **Macro link:** input-cost inflation; rate-sensitive CAPEX; productivity focus matters  
- **Opportunity:** precision farming, climate-smart tech, automation, premium processing  
- **Risks:** climate volatility, commodity cycles  
- **Policy support:** sustainability and modernization incentives
""")
