"""
TEA Web App - Technoeconomic Analysis for Geothermal / CO2 Sequestration
Updated to reflect NEW TEA Model.ipynb (260211 Technoeconomics.xlsx structure)
"""
import io
import streamlit as st
import pandas as pd
from model import technoeconomics_analysis

st.set_page_config(page_title="TEA Model", page_icon="⚡", layout="wide")
st.title("⚡ Dualwell Technoeconomic Analysis")
st.markdown("*Updated from NEW TEA Model (260211 Technoeconomics.xlsx)*")
st.divider()

# Base case defaults from NEW TEA Model.ipynb
DEFAULTS = {
    "captured_and_stored_mtpa": 0.2,
    "percent_sequestered": 0.01,
    "max_injection_rate_per_well": 100.0,
    "thermal_extraction_mwt_kgs": 0.711,
    "thermal_efficiency": 0.18,
    "capacity_factor": 0.9,
    "cost_of_capital": 0.08,
    "project_life_years": 15,
    "capex_escalation_factor": 1.0,
    "tax_rate": 0.21,
    "carbon_price_above_45q": 40.0,
    "co2_cost_per_tonne": 100.0,
    "tax_credit_45q": 85.0,
    "power_value_usd_mwh": 80.0,
    "above_ground_capex_base_m": 111.1,
    "reference_power_mwe": 87.1,
    "drilling_cost_per_well_m": 4.0,
    "stimulation_cost_per_well_m": 4.0,
    "exploration_cost_m": 30.0,
    "annual_salaries_m": 1.5,
    "maintenance_per_well_m": 0.04,
    "opex_per_mw_m": 0.04,
    "redrilling_per_well_m": 0.855,
}

# Initialize session state for runs history
if "runs" not in st.session_state:
    st.session_state.runs = []

with st.form("tea_inputs"):
    st.subheader("Model Inputs")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Design Inputs**")
        captured_and_stored_mtpa = st.number_input(
            "CO2 sequestered (Mtpa)",
            min_value=0.01,
            max_value=10.0,
            value=DEFAULTS["captured_and_stored_mtpa"],
            step=0.01,
            format="%.2f",
            help="Basis for project sizing - assumes constant CO2 supply rate (base case: 0.2 Mtpa)",
        )
        percent_sequestered_pct = st.number_input(
            "Injection CO2 % sequestered",
            min_value=0.1,
            max_value=100.0,
            value=1.0,
            step=0.1,
            format="%.1f",
            help="% of injected CO2 that is sequestered/lost to subsurface (base case: 1%)",
        )
        percent_sequestered = percent_sequestered_pct / 100
        max_injection_rate_per_well = st.number_input(
            "Max injection rate per well (kg/s)",
            min_value=50.0,
            max_value=150.0,
            value=DEFAULTS["max_injection_rate_per_well"],
            step=10.0,
            format="%.0f",
        )
        thermal_extraction_mwt_kgs = st.number_input(
            "Thermal extraction (MWt/(kg/s))",
            min_value=0.3,
            max_value=1.5,
            value=DEFAULTS["thermal_extraction_mwt_kgs"],
            step=0.01,
            format="%.3f",
            help="Heat extracted per unit mass flow from reservoir (base case: 0.71 MWt/(kg/s))",
        )
        thermal_efficiency_pct = st.number_input(
            "Thermal efficiency (%)",
            min_value=5.0,
            max_value=40.0,
            value=18.0,
            step=0.5,
            format="%.1f",
            help="Amount of heat extracted from geothermal reservoir converted to power (base case: 18%)",
        )
        thermal_efficiency = thermal_efficiency_pct / 100
        capacity_factor = st.number_input(
            "Capacity factor",
            min_value=0.5,
            max_value=1.0,
            value=DEFAULTS["capacity_factor"],
            step=0.05,
            format="%.2f",
            help="1.0 = 8760 hrs; 0.9 = 7884 hrs",
        )

    with c2:
        st.markdown("**Financial & Revenue**")
        cost_of_capital_pct = st.number_input(
            "Cost of capital (%)",
            min_value=1.0,
            max_value=30.0,
            value=8.0,
            step=0.5,
            format="%.1f",
        )
        cost_of_capital = cost_of_capital_pct / 100
        project_life_years = st.number_input(
            "Project lifetime (years)",
            min_value=5,
            max_value=50,
            value=DEFAULTS["project_life_years"],
            step=1,
            format="%d",
            help="Project lifetime in years (base case: 15 years)",
        )
        capex_escalation_factor = st.number_input(
            "Capex escalation factor",
            min_value=0.5,
            max_value=1.5,
            value=DEFAULTS["capex_escalation_factor"],
            step=0.1,
            format="%.1f",
            help="1.0 = base, 1.2 = high cost, 0.8 = low cost",
        )
        tax_rate_pct = st.number_input(
            "Tax rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=21.0,
            step=1.0,
            format="%.1f",
        )
        tax_rate = tax_rate_pct / 100
        power_value_usd_mwh = st.number_input(
            "Power price ($/MWh)",
            min_value=0.0,
            max_value=500.0,
            value=DEFAULTS["power_value_usd_mwh"],
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
            help="Carbon price for CO2 sequestration credits (base case: $40/tonne)",
        )
        co2_cost_per_tonne = st.number_input(
            "CO2 procurement cost ($/tonne)",
            min_value=0.0,
            max_value=300.0,
            value=DEFAULTS["co2_cost_per_tonne"],
            step=10.0,
            format="%.1f",
            help="Cost of CO2 procurement, assumed to be via carbon capture from anthropogenic sources (base case: $100/tonne)",
        )

    with c3:
        st.markdown("**Capex & O&M**")
        above_ground_capex_base_m = st.number_input(
            "Above-ground capex  ($M)",
            min_value=50.0,
            max_value=200.0,
            value=DEFAULTS["above_ground_capex_base_m"],
            step=5.0,
            format="%.1f",
            help="Power plant and above-ground capex (base case from NREL sCO2 cycle + contingency: $111.1M)",
        )
        drilling_cost_per_well_m = st.number_input(
            "Drilling cost per well ($M)",
            min_value=1.0,
            max_value=10.0,
            value=DEFAULTS["drilling_cost_per_well_m"],
            step=0.5,
            format="%.1f",
            help="Subsurface capex per well for drilling, completion, and infrastructure (base case comes from GEOPHIRES Fervo Cape Station project: $4M)",
        )
        stimulation_cost_per_well_m = st.number_input(
            "Stimulation cost per well ($M)",
            min_value=1.0,
            max_value=10.0,
            value=DEFAULTS["stimulation_cost_per_well_m"],
            step=0.5,
            format="%.1f",
            help="Subsurface capex per well for stimulation (base case comes from GEOPHIRES Fervo Cape Station project: $4M)",
        )
        exploration_cost_m = st.number_input(
            "Exploration cost ($M)",
            min_value=0.0,
            max_value=100.0,
            value=DEFAULTS["exploration_cost_m"],
            step=5.0,
            format="%.1f",
            help="Subsurface capex for exploration and development (base case comes from GEOPHIRES Fervo Cape Station project: $30M)",
        )
        annual_salaries_m = st.number_input(
            "Annual salaries ($M)",
            min_value=0.5,
            max_value=5.0,
            value=DEFAULTS["annual_salaries_m"],
            step=0.1,
            format="%.1f",
            help="Annual salaries for project operations (base case: 10 employees @ $150k/year = $1.5M)",
        )
        maintenance_per_well_m = st.number_input(
            "Maintenance per well ($M/yr)",
            min_value=0.01,
            max_value=0.1,
            value=DEFAULTS["maintenance_per_well_m"],
            step=0.01,
            format="%.2f",
            help="Maintenance cost per well per year (base case comes from GEOPHIRES Fervo Cape Station project: $0.04M/well/year)",
        )
        opex_per_mw_m = st.number_input(
            "Power plant opex per MW ($M/yr)",
            min_value=0.01,
            max_value=0.1,
            value=DEFAULTS["opex_per_mw_m"],
            step=0.01,
            format="%.2f",
            help="Power plant operating expenses per MW of installed capacity per year (base case comes from GEOPHIRES Fervo Cape Station project: $0.04M/MW/year)",
        )
        redrilling_per_well_m = st.number_input(
            "Redrilling cost per well ($M/yr)",
            min_value=0.3,
            max_value=2.0,
            value=DEFAULTS["redrilling_per_well_m"],
            step=0.05,
            format="%.2f",
            help="Redrilling cost per well per year (base case comes from GEOPHIRES Fervo Cape Station project: $0.855M/well/year)",
        )

    tax_credit_45q = DEFAULTS["tax_credit_45q"]
    reference_power_mwe = DEFAULTS["reference_power_mwe"]  # Fixed for above-ground scaling

    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        metrics = technoeconomics_analysis(
            captured_and_stored_mtpa=captured_and_stored_mtpa,
            percent_sequestered=percent_sequestered,
            max_injection_rate_per_well=max_injection_rate_per_well,
            thermal_extraction_mwt_kgs=thermal_extraction_mwt_kgs,
            thermal_efficiency=thermal_efficiency,
            capacity_factor=capacity_factor,
            cost_of_capital=cost_of_capital,
            project_life_years=int(project_life_years),
            capex_escalation_factor=capex_escalation_factor,
            tax_rate=tax_rate,
            carbon_price_above_45q=carbon_price_above_45q,
            co2_cost_per_tonne=co2_cost_per_tonne,
            tax_credit_45q=tax_credit_45q,
            power_value_usd_mwh=power_value_usd_mwh,
            above_ground_capex_base_m=above_ground_capex_base_m,
            reference_power_mwe=reference_power_mwe,
            drilling_cost_per_well_m=drilling_cost_per_well_m,
            stimulation_cost_per_well_m=stimulation_cost_per_well_m,
            exploration_cost_m=exploration_cost_m,
            annual_salaries_m=annual_salaries_m,
            maintenance_per_well_m=maintenance_per_well_m,
            opex_per_mw_m=opex_per_mw_m,
            redrilling_per_well_m=redrilling_per_well_m,
        )

        # Append run to history
        run_data = {
            "CO2 sequestered (Mtpa)": captured_and_stored_mtpa,
            "Injection CO2 % sequestered": percent_sequestered_pct,
            "Max injection rate (kg/s)": max_injection_rate_per_well,
            "Thermal extraction (MWt/(kg/s))": thermal_extraction_mwt_kgs,
            "Thermal efficiency (%)": thermal_efficiency_pct,
            "Capacity factor": capacity_factor,
            "Cost of capital (%)": cost_of_capital_pct,
            "Project lifetime (years)": project_life_years,
            "Power price ($/MWh)": power_value_usd_mwh,
            "Carbon price ($/tonne)": carbon_price_above_45q,
            "CO2 cost ($/tonne)": co2_cost_per_tonne,
            "Above-ground capex ($M)": above_ground_capex_base_m,
            "Drilling cost ($M/well)": drilling_cost_per_well_m,
            "Stimulation cost ($M/well)": stimulation_cost_per_well_m,
            "LCOE ($/MWh)": metrics["LCOE"],
            "NPV ($M)": metrics["NPV"],
            "IRR (%)": metrics["IRR"] * 100 if metrics["IRR"] is not None else None,
            "Payback (years)": metrics["Payback"],
        }
        st.session_state.runs.append(run_data)

        st.divider()
        st.subheader("Results")
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.metric("LCOE", f"${metrics['LCOE']:,.2f}", "/MWh")
        with r2:
            st.metric("Post-tax NPV", f"${metrics['NPV']:,.2f} M", "Million USD")
        with r3:
            irr_str = f"{metrics['IRR']:.2%}" if metrics["IRR"] is not None else "N/A"
            st.metric("IRR", irr_str, "")
        with r4:
            payback_str = f"{metrics['Payback']} yrs" if metrics["Payback"] is not None else "N/A"
            st.metric("Payback", payback_str, "")

        with st.expander("Design Summary"):
            st.write(f"**Power:** {metrics['power_generated_mw']:.2f} MWe | **Energy:** {metrics['annual_energy_mwh']:,.0f} MWh/yr")
            st.write(f"**Wells:** {metrics['total_wells']} total | **Capex:** ${metrics['total_capex_m']:,.1f} M (Above-ground: ${metrics['above_ground_m']:,.1f} M, Subsurface: ${metrics['subsurface_m']:,.1f} M)")

    except Exception as e:
        st.error(f"Error running model: {e}")

# Runs table at bottom
st.divider()
st.subheader("Run History")
st.markdown("Each column represents one run with all inputs and outputs.")

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
        st.download_button(
            "📥 Export to Excel",
            data=b"",
            file_name="TEA_Runs.xlsx",
            disabled=True,
            key="download_disabled",
        )
with btn_col2:
    if st.button("🗑️ Clear Table", disabled=len(st.session_state.runs) == 0, key="clear_table"):
        st.session_state.runs = []
        st.rerun()

if st.session_state.runs:
    df_runs = pd.DataFrame(st.session_state.runs)
    df_runs = df_runs.T
    df_runs.columns = [f"Run_{i + 1}" for i in range(len(df_runs.columns))]
    df_runs.index.name = "Parameter"
    st.dataframe(df_runs, use_container_width=True, height=min(400, 50 + 35 * len(df_runs)))
else:
    st.info("No runs yet. Use the form above and click **Calculate** to add runs.")
