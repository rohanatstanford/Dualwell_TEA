"""
Technoeconomic Analysis (TEA) Model for Geothermal / CO2 Sequestration
Extracted from NEW TEA Model.ipynb (260211 Technoeconomics.xlsx structure)
"""
import numpy as np
import numpy_financial as npf

# Constants from notebook
CAPEX_SCHEDULE = [0.33, 0.33, 0.34]
START_OPERATIONS_YEAR = 3
TAX_CREDIT_DURATION_YEARS = 12


def technoeconomics_analysis(
    captured_and_stored_mtpa: float,
    percent_sequestered: float,
    max_injection_rate_per_well: float,
    thermal_extraction_mwt_kgs: float,
    thermal_efficiency: float,
    capacity_factor: float,
    cost_of_capital: float,
    project_life_years: int,
    capex_escalation_factor: float,
    tax_rate: float,
    carbon_price_above_45q: float,
    co2_cost_per_tonne: float,
    tax_credit_45q: float,
    power_value_usd_mwh: float,
    above_ground_capex_base_m: float,
    reference_power_mwe: float,
    drilling_cost_per_well_m: float,
    stimulation_cost_per_well_m: float,
    exploration_cost_m: float,
    annual_salaries_m: float,
    maintenance_per_well_m: float,
    opex_per_mw_m: float,
    redrilling_per_well_m: float,
) -> dict:
    """Run TEA and return post-tax + pre-tax metrics."""
    hours = 8760 * capacity_factor
    total_years = START_OPERATIONS_YEAR + project_life_years
    years = np.arange(total_years)

    # 1. Injection rate and wells
    injected_co2_mtpa = captured_and_stored_mtpa / percent_sequestered
    total_injection_rate_kgs = (injected_co2_mtpa * 1e9) / (8760 * 3600)
    num_injection_wells = int(np.ceil(total_injection_rate_kgs / max_injection_rate_per_well))
    num_production_wells = num_injection_wells
    total_wells = num_injection_wells + num_production_wells

    # 2. Heat and power
    heat_generated_mwt = total_injection_rate_kgs * thermal_extraction_mwt_kgs
    power_generated_mw = heat_generated_mwt * thermal_efficiency
    annual_energy_mwh = power_generated_mw * hours

    # 3. Capex
    above_ground_m = (
        above_ground_capex_base_m
        * (power_generated_mw)
        * capex_escalation_factor
    )
    well_cost_m = (drilling_cost_per_well_m + stimulation_cost_per_well_m) * total_wells
    subsurface_m = (well_cost_m + exploration_cost_m) * capex_escalation_factor
    total_capex_m = above_ground_m + subsurface_m

    # 4. Opex (annual)
    salaries_m = annual_salaries_m
    wellfield_maint_m = maintenance_per_well_m * total_wells
    power_plant_opex_m = opex_per_mw_m * power_generated_mw
    redrilling_m = redrilling_per_well_m * total_wells
    annual_opex_m = salaries_m + wellfield_maint_m + power_plant_opex_m + redrilling_m

    # Initialize arrays
    capex_flows = np.zeros(total_years)
    revenue_elec = np.zeros(total_years)
    revenue_45q = np.zeros(total_years)
    revenue_carbon = np.zeros(total_years)
    opex_flows = np.zeros(total_years)
    co2_cost_flows = np.zeros(total_years)

    # Capex (years 0-2)
    for i, share in enumerate(CAPEX_SCHEDULE):
        if i < total_years:
            capex_flows[i] = -share * total_capex_m

    end_ops = START_OPERATIONS_YEAR + project_life_years
    end_45q = START_OPERATIONS_YEAR + TAX_CREDIT_DURATION_YEARS

    for yr in range(START_OPERATIONS_YEAR, end_ops):
        if yr >= total_years:
            break
        revenue_elec[yr] = (annual_energy_mwh * power_value_usd_mwh) / 1e6
        if yr < end_45q:
            revenue_45q[yr] = captured_and_stored_mtpa * tax_credit_45q * capacity_factor
        revenue_carbon[yr] = captured_and_stored_mtpa * carbon_price_above_45q * capacity_factor
        opex_flows[yr] = -annual_opex_m
        co2_cost_flows[yr] = -captured_and_stored_mtpa * co2_cost_per_tonne * capacity_factor

    # Taxable income: use EBIT for tax
    ebit = capex_flows + revenue_elec + revenue_45q + revenue_carbon + opex_flows + co2_cost_flows
    taxable_income = ebit

    # Tax: negative taxable -> positive tax_cash (credit received)
    tax_cash = -tax_rate * taxable_income

    # Pre-tax and post-tax cash flow
    pre_tax_cash_flow = (
        capex_flows
        + revenue_elec
        + revenue_45q
        + revenue_carbon
        + opex_flows
        + co2_cost_flows
    )
    net_cash_flow = pre_tax_cash_flow + tax_cash

    discount_factors = 1 / ((1 + cost_of_capital) ** years)
    discounted_cf = net_cash_flow * discount_factors
    pre_tax_discounted_cf = pre_tax_cash_flow * discount_factors

    npv = discounted_cf.sum()
    pre_tax_npv = pre_tax_discounted_cf.sum()
    cumulative = np.cumsum(net_cash_flow)
    payback = next((i for i, x in enumerate(cumulative) if x >= 0), None)

    generation_flows = np.zeros(total_years)
    for yr in range(START_OPERATIONS_YEAR, end_ops):
        if yr < total_years:
            generation_flows[yr] = annual_energy_mwh
    discounted_gen = np.sum(generation_flows * discount_factors)
    npv_elec = np.sum(revenue_elec * discount_factors)
    npv_non_elec = npv - npv_elec
    pre_tax_npv_non_elec = pre_tax_npv - npv_elec
    lcoe = (-npv_non_elec * 1e6) / discounted_gen if discounted_gen > 0 else 0.0
    lcoe_pre_tax = (
        (-pre_tax_npv_non_elec * 1e6) / discounted_gen if discounted_gen > 0 else 0.0
    )

    irr = None
    try:
        irr = npf.irr(net_cash_flow)
    except Exception:
        pass

    return {
        "LCOE": lcoe,
        "LCOE_pre_tax": lcoe_pre_tax,
        "LCOE_post_tax": lcoe,
        "NPV": npv,
        "IRR": irr,
        "Payback": payback,
        "power_generated_mw": power_generated_mw,
        "annual_energy_mwh": annual_energy_mwh,
        "total_wells": total_wells,
        "total_capex_m": total_capex_m,
        "above_ground_m": above_ground_m,
        "subsurface_m": subsurface_m,
    }
