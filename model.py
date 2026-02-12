"""
Technoeconomic Analysis (TEA) Model for Geothermal / CO2 Sequestration
Extracted from TEA Model.ipynb
"""
import numpy as np
import numpy_financial as npf


def technoeconomics_analysis(
    captured_and_stored_mtpa: float,
    percent_sequestered: float,
    co2_water_ratio: float,
    sco2_capex_m: float,
    geo_capex_per_well_m: float,
    cost_of_capital: float,
    power_value_usd_mwh: float,
    thermal_efficiency: float,
    thermal_extraction_mwt_kgs: float,
    annual_opex_m: float,
    carbon_price_above_45q: float,
    co2_cost_per_tonne: float,
    operating_life_years: int = 15,  # Project lifetime in years
    tax_credit_duration_years: int = 12,
    capacity_factor: float = 1.0,
) -> dict:
    """Run TEA and return LCOE, NPV, IRR, Payback."""
    tax_credit_45q = 85.0  # $/tonne
    hours_per_year = 8160 * capacity_factor
    capex_schedule = [1 / 3, 1 / 3, 1 / 3]
    start_operations_year = 3
    total_years_analysis = start_operations_year + operating_life_years
    years = np.arange(total_years_analysis)

    # 1. Total CO2 Injection Rate
    injected_co2_mtpa = captured_and_stored_mtpa / percent_sequestered
    total_injection_rate_kgs = (injected_co2_mtpa * 1e9) / (hours_per_year * 3600) / co2_water_ratio

    # 2. Total Geothermal Capex
    num_injection_wells = np.ceil(total_injection_rate_kgs / 100.0)
    total_wells = 2 * num_injection_wells
    total_geo_capex_m = total_wells * geo_capex_per_well_m
    total_capex_m = sco2_capex_m + total_geo_capex_m

    # 3. Heat and Power Generation
    heat_generated_mwt = total_injection_rate_kgs * thermal_extraction_mwt_kgs
    power_generated_mw = heat_generated_mwt * thermal_efficiency
    annual_energy_mwh = power_generated_mw * hours_per_year

    capex_flows = np.zeros(total_years_analysis)
    revenue_elec = np.zeros(total_years_analysis)
    revenue_45q = np.zeros(total_years_analysis)
    revenue_carbon_credit = np.zeros(total_years_analysis)
    opex_flows = np.zeros(total_years_analysis)
    co2_cost_flows = np.zeros(total_years_analysis)

    for i, share in enumerate(capex_schedule):
        if i < total_years_analysis:
            capex_flows[i] = -1 * share * total_capex_m

    end_ops_year = start_operations_year + operating_life_years
    end_45q_year = start_operations_year + tax_credit_duration_years

    for yr in range(start_operations_year, end_ops_year):
        if yr >= total_years_analysis:
            break
        revenue_elec[yr] = (annual_energy_mwh * power_value_usd_mwh) / 1e6
        if yr < end_45q_year:
            revenue_45q[yr] = captured_and_stored_mtpa * tax_credit_45q
        revenue_carbon_credit[yr] = captured_and_stored_mtpa * carbon_price_above_45q
        opex_flows[yr] = -1 * annual_opex_m
        co2_cost_flows[yr] = -1 * captured_and_stored_mtpa * co2_cost_per_tonne

    net_cash_flow = capex_flows + revenue_elec + revenue_45q + revenue_carbon_credit + opex_flows + co2_cost_flows
    discount_factors = 1 / ((1 + cost_of_capital) ** years)
    discounted_cash_flow = net_cash_flow * discount_factors

    cumulative_cash_flow = np.cumsum(net_cash_flow)
    payback_period = next((i for i, x in enumerate(cumulative_cash_flow) if x >= 0), None)

    generation_flows = np.zeros(total_years_analysis)
    for yr in range(start_operations_year, end_ops_year):
        if yr >= total_years_analysis:
            break
        generation_flows[yr] = annual_energy_mwh

    discounted_generation = np.sum(generation_flows * discount_factors)
    npv = discounted_cash_flow.sum()
    npv_elec_revenue = np.sum(revenue_elec * discount_factors)
    npv_non_elec = npv - npv_elec_revenue

    if discounted_generation > 0:
        lcoe = (-1 * npv_non_elec * 1e6) / discounted_generation
    else:
        lcoe = 0.0

    irr = None
    try:
        irr = npf.irr(net_cash_flow)
    except Exception:
        pass

    return {
        "LCOE": lcoe,
        "NPV": npv,
        "IRR": irr,
        "Payback": payback_period,
    }
