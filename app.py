"""
TEA Web App - Technoeconomic Analysis for Geothermal / CO2 Sequestration
"""
import io
import streamlit as st
import pandas as pd
from model import technoeconomics_analysis

st.set_page_config(page_title="TEA Model", page_icon="⚡", layout="wide")
st.title("⚡ DualWell Technoeconomic Analysis")
st.markdown("*11 Feb 2026*")
st.divider()

# Base case defaults from TEA Model.ipynb
DEFAULTS = {
    "captured_and_stored_mtpa": 0.2,
    "percent_sequestered": 0.01,
    "co2_water_ratio": 1.0,
    "sco2_capex_m": 70.0,
    "geo_capex_per_well_m": 10.0,
    "cost_of_capital": 0.08,
    "power_value_usd_mwh": 95.4,
    "thermal_efficiency": 0.19,
    "thermal_extraction_mwt_kgs": 52.88 / 74.38,
    "annual_opex_m": 30.0,
    "carbon_price_above_45q": 40.0,
    "co2_cost_per_tonne": 100.0,
    "operating_life_years": 15,
    "tax_credit_duration_years": 12,
}

# Initialize session state for runs history
if "runs" not in st.session_state:
    st.session_state.runs = []

with st.form("tea_inputs"):
    st.subheader("Model Inputs")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**CO2 Parameters**")
        captured_and_stored_mtpa = st.number_input(
            "Captured and stored (Mtpa)",
            min_value=0.01,
            max_value=10.0,
            value=DEFAULTS["captured_and_stored_mtpa"],
            step=0.01,
            format="%.2f",
            help="Amount permanently sequestered",
        )
        percent_sequestered_pct = st.number_input(
            "Injection CO2 % sequestered",
            min_value=0.1,
            max_value=100.0,
            value=1.0,
            step=0.1,
            format="%.1f",
            help="% of injected CO2 that is sequestered",
        )
        percent_sequestered = percent_sequestered_pct / 100
        co2_water_ratio = st.number_input(
            "CO2/Water ratio",
            min_value=0.1,
            max_value=5.0,
            value=DEFAULTS["co2_water_ratio"],
            step=0.1,
            format="%.1f",
        )

    with c2:
        st.markdown("**Financial**")
        sco2_capex_m = st.number_input(
            "sCO2 Capex ($M)",
            min_value=10.0,
            max_value=500.0,
            value=DEFAULTS["sco2_capex_m"],
            step=5.0,
            format="%.1f",
        )
        geo_capex_per_well_m = st.number_input(
            "Geothermal capex per well ($M)",
            min_value=1.0,
            max_value=50.0,
            value=DEFAULTS["geo_capex_per_well_m"],
            step=1.0,
            format="%.1f",
        )
        cost_of_capital_pct = st.number_input(
            "Cost of capital (%)",
            min_value=1.0,
            max_value=30.0,
            value=8.0,
            step=0.5,
            format="%.1f",
        )
        cost_of_capital = cost_of_capital_pct / 100
        power_value_usd_mwh = st.number_input(
            "Power price ($/MWh)",
            min_value=0.0,
            max_value=500.0,
            value=DEFAULTS["power_value_usd_mwh"],
            step=5.0,
            format="%.1f",
        )

    with c3:
        st.markdown("**Operations**")
        thermal_efficiency_pct = st.number_input(
            "Thermal efficiency (%)",
            min_value=5.0,
            max_value=50.0,
            value=19.0,
            step=0.5,
            format="%.1f",
        )
        thermal_efficiency = thermal_efficiency_pct / 100
        thermal_extraction_mwt_kgs = st.number_input(
            "Thermal extraction (MWt/(kg/s))",
            min_value=0.1,
            max_value=2.0,
            value=round(DEFAULTS["thermal_extraction_mwt_kgs"], 4),
            step=0.01,
            format="%.4f",
        )
        annual_opex_m = st.number_input(
            "Annual opex ($M/year)",
            min_value=0.0,
            max_value=200.0,
            value=DEFAULTS["annual_opex_m"],
            step=5.0,
            format="%.1f",
        )
        carbon_price_above_45q = st.number_input(
            "Carbon price above 45Q ($/tonne)",
            min_value=0.0,
            max_value=200.0,
            value=DEFAULTS["carbon_price_above_45q"],
            step=5.0,
            format="%.1f",
        )
        co2_cost_per_tonne = st.number_input(
            "CO2 cost ($/tonne)",
            min_value=0.0,
            max_value=300.0,
            value=DEFAULTS["co2_cost_per_tonne"],
            step=10.0,
            format="%.1f",
        )

    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        metrics = technoeconomics_analysis(
            captured_and_stored_mtpa=captured_and_stored_mtpa,
            percent_sequestered=percent_sequestered,
            co2_water_ratio=co2_water_ratio,
            sco2_capex_m=sco2_capex_m,
            geo_capex_per_well_m=geo_capex_per_well_m,
            cost_of_capital=cost_of_capital,
            power_value_usd_mwh=power_value_usd_mwh,
            thermal_efficiency=thermal_efficiency,
            thermal_extraction_mwt_kgs=thermal_extraction_mwt_kgs,
            annual_opex_m=annual_opex_m,
            carbon_price_above_45q=carbon_price_above_45q,
            co2_cost_per_tonne=co2_cost_per_tonne,
            operating_life_years=DEFAULTS["operating_life_years"],
            tax_credit_duration_years=DEFAULTS["tax_credit_duration_years"],
        )

        # Append run to history (inputs + outputs)
        run_data = {
            "Captured and stored (Mtpa)": captured_and_stored_mtpa,
            "Injection CO2 % sequestered": percent_sequestered_pct,
            "CO2/Water ratio": co2_water_ratio,
            "sCO2 Capex ($M)": sco2_capex_m,
            "Geothermal capex per well ($M)": geo_capex_per_well_m,
            "Cost of capital (%)": cost_of_capital_pct,
            "Power price ($/MWh)": power_value_usd_mwh,
            "Thermal efficiency (%)": thermal_efficiency_pct,
            "Thermal extraction (MWt/(kg/s))": thermal_extraction_mwt_kgs,
            "Annual opex ($M/year)": annual_opex_m,
            "Carbon price above 45Q ($/tonne)": carbon_price_above_45q,
            "CO2 cost ($/tonne)": co2_cost_per_tonne,
            "LCOE ($/MWh)": metrics["LCOE"],
            "NPV ($M)": metrics["NPV"],
            "IRR (%)": metrics["IRR"] * 100 if metrics["IRR"] is not None else None,
        }
        st.session_state.runs.append(run_data)

        st.divider()
        st.subheader("Results")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("LCOE", f"${metrics['LCOE']:,.2f}", "/MWh")
        with r2:
            st.metric("NPV", f"${metrics['NPV']:,.2f} M", "Million USD")
        with r3:
            irr_str = f"{metrics['IRR']:.2%}" if metrics["IRR"] is not None else "N/A"
            st.metric("IRR", irr_str, "")

    except Exception as e:
        st.error(f"Error running model: {e}")

# Runs table at bottom
st.divider()
st.subheader("Run History")
st.markdown("Each column represents one run with all inputs and outputs.")

# Export and Clear buttons
btn_col1, btn_col2, _ = st.columns([1, 1, 4])
with btn_col1:
    if st.session_state.runs:
        df_runs = pd.DataFrame(st.session_state.runs)
        df_runs = df_runs.T
        df_runs.columns = [f"Run_{i + 1}" for i in range(len(df_runs.columns))]
        df_runs.index.name = "Parameter"
        buffer = io.BytesIO()
        df_runs.to_excel(buffer, index=True)
        buffer.seek(0)
        st.download_button(
            label="📥 Export to Excel",
            data=buffer,
            file_name="TEA_Runs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel",
        )
    else:
        st.download_button("📥 Export to Excel", data=b"", file_name="TEA_Runs.xlsx", disabled=True, key="download_disabled")
with btn_col2:
    if st.button("🗑️ Clear Table", disabled=len(st.session_state.runs) == 0, key="clear_table"):
        st.session_state.runs = []
        st.rerun()

# Runs table
if st.session_state.runs:
    df_runs = pd.DataFrame(st.session_state.runs)
    df_runs = df_runs.T
    df_runs.columns = [f"Run_{i + 1}" for i in range(len(df_runs.columns))]
    df_runs.index.name = "Parameter"
    st.dataframe(df_runs, use_container_width=True, height=min(400, 50 + 35 * len(df_runs)))
else:
    st.info("No runs yet. Use the form above and click **Calculate** to add runs.")
