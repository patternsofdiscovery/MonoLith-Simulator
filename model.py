def clamp(value, low, high):
    return max(low, min(high, value))


def run_model(inputs):
    feed_mode = inputs["feed_mode"]
    flow_m3h = inputs["flow_m3h"]
    li_conc = inputs["li_conc"]
    uptime = inputs["uptime"]

    mg_gl = inputs["mg_gl"]
    ca_gl = inputs["ca_gl"]
    na_gl = inputs["na_gl"]
    k_gl = inputs["k_gl"]
    so4_gl = inputs["so4_gl"]
    b_gl = inputs["b_gl"]

    li_capture = inputs["li_capture"]
    wash_recovery = inputs["wash_recovery"]
    polish_efficiency = inputs["polish_efficiency"]

    faradaic_eff = inputs["faradaic_eff"]
    current_density = inputs["current_density"]
    cell_voltage = inputs["cell_voltage"]
    current_per_stack = inputs["current_per_stack"]
    active_area_per_stack = inputs["active_area_per_stack"]
    stack_count = inputs["stack_count"]
    conversion_per_pass = inputs["conversion_per_pass"]
    recycle_ratio = inputs["recycle_ratio"]

    crystallizer_yield = inputs["crystallizer_yield"]
    mother_liquor_recovery = inputs["mother_liquor_recovery"]
    target_purity = inputs["target_purity"]

    power_price = inputs["power_price"]
    reagent_cost_ton = inputs["reagent_cost_ton"]
    labor_maint_ton = inputs["labor_maint_ton"]
    capex_m = inputs["capex_m"]
    project_years = inputs["project_years"]

    if feed_mode == "LiCl":
        route_name = "LiCl route"
        electrochem_multiplier = 1.00
        crystallization_bias = 1.00
        sulfate_penalty = 1.00
        reagent_bias = 1.00
        voltage_bias = 4.2
        purity_bias = 0.04
    else:
        route_name = "Li2SO4 route"
        electrochem_multiplier = 0.94
        crystallization_bias = 0.985
        sulfate_penalty = 1.18
        reagent_bias = 1.08
        voltage_bias = 4.8
        purity_bias = -0.03

    F = 96485.0
    MW_LI = 6.94
    MW_LIOH_H2O = 41.96

    annual_hours = 8760.0 * (uptime / 100.0)

    li_feed_kg_h = flow_m3h * li_conc
    li_feed_mol_h = (li_feed_kg_h * 1000.0) / MW_LI

    if feed_mode == "LiCl":
        chloride_equivalent_gl = li_conc * (35.45 / 6.94)
        sulfate_equivalent_gl = 0.0
    else:
        chloride_equivalent_gl = 0.0
        sulfate_equivalent_gl = li_conc * (48.03 / 6.94)

    effective_sulfate_gl = so4_gl + sulfate_equivalent_gl

    divalent_severity = mg_gl * 1.6 + ca_gl * 1.5
    anion_severity = (
        effective_sulfate_gl * 0.8 * sulfate_penalty
        + b_gl * 1.1
        + chloride_equivalent_gl * 0.02
    )
    alkali_severity = na_gl * 0.08 + k_gl * 0.12
    impurity_severity = divalent_severity + anion_severity + alkali_severity

    adjusted_polish = clamp(polish_efficiency / 100.0, 0.0, 0.995)
    impurity_penalty = clamp(
        1.0 - impurity_severity * 0.025 * (1.0 - adjusted_polish),
        0.72,
        1.0,
    )

    capture_recovery = (li_capture / 100.0) * (wash_recovery / 100.0)
    li_captured_kg_h = li_feed_kg_h * capture_recovery
    li_captured_mol_h = (li_captured_kg_h * 1000.0) / MW_LI

    installed_current_a = current_per_stack * stack_count
    theoretical_li_mol_h = installed_current_a * 3600.0 / F
    electrochem_capacity_mol_h = (
        theoretical_li_mol_h * (faradaic_eff / 100.0) * electrochem_multiplier
    )

    recycle_multiplier = 1.0 + recycle_ratio * 0.10
    effective_pass_conversion = (conversion_per_pass / 100.0) * recycle_multiplier
    conversion_adjusted = clamp(effective_pass_conversion, 0.45, 0.985)

    lithium_through_ec_mol_h = min(
        li_captured_mol_h * impurity_penalty,
        electrochem_capacity_mol_h / max(conversion_adjusted, 0.01),
    )

    li_converted_mol_h = lithium_through_ec_mol_h * conversion_adjusted
    li_converted_kg_h = (li_converted_mol_h * MW_LI) / 1000.0

    primary_crystal_yield = (crystallizer_yield / 100.0) * crystallization_bias
    mother_liquor_bonus = (1.0 - primary_crystal_yield) * (
        mother_liquor_recovery / 100.0
    )
    effective_crystallization_yield = clamp(
        primary_crystal_yield + mother_liquor_bonus,
        0.75,
        0.995,
    )

    li_to_product_kg_h = li_converted_kg_h * effective_crystallization_yield
    lioh_kg_h_unconstrained = li_to_product_kg_h * (MW_LIOH_H2O / MW_LI)

    required_area_m2 = installed_current_a / max(current_density, 1.0)
    provided_area_m2 = active_area_per_stack * stack_count
    area_constraint = clamp(
        provided_area_m2 / max(required_area_m2, 0.0001),
        0.0,
        1.2,
    )
    area_limited_factor = min(area_constraint, 1.0)

    lioh_kg_h = lioh_kg_h_unconstrained * area_limited_factor
    lioh_tpy = (lioh_kg_h * annual_hours) / 1000.0

    route_adjusted_voltage = (cell_voltage + voltage_bias) / 2.0
    power_kw = installed_current_a * route_adjusted_voltage / 1000.0
    annual_energy_mwh = power_kw * annual_hours / 1000.0

    annual_product_ton = max(lioh_tpy, 1.0)
    annual_product_kg = annual_product_ton * 1000.0

    specific_energy_kwh_kg = (annual_energy_mwh * 1000.0) / annual_product_kg
    specific_energy_kwh_ton = specific_energy_kwh_kg * 1000.0

    electricity_price_usd_mwh = power_price
    electricity_price_usd_kwh = electricity_price_usd_mwh / 1000.0
    power_cost_ton = specific_energy_kwh_ton * electricity_price_usd_kwh

    residual_impurity_index = (
        impurity_severity
        * (1.0 - polish_efficiency / 100.0)
        * (1.0 - (conversion_per_pass / 100.0) * 0.35)
    )
    purity_proxy = clamp(
        target_purity - residual_impurity_index * 0.08 + purity_bias,
        97.5,
        99.9,
    )

    route_adjusted_reagent_cost = reagent_cost_ton * reagent_bias
    opex_ton = power_cost_ton + route_adjusted_reagent_cost + labor_maint_ton
    annualized_capex = (capex_m * 1_000_000.0) / project_years
    cash_cost_ton = opex_ton + annualized_capex / max(lioh_tpy, 1.0)

    utilization_pct = clamp(
        (li_converted_mol_h / max(electrochem_capacity_mol_h, 1e-9)) * 100.0,
        0.0,
        100.0,
    )

    if area_constraint < 0.98:
        bottleneck = "Membrane area / stack geometry"
    elif electrochem_capacity_mol_h < li_captured_mol_h * conversion_adjusted:
        bottleneck = "Installed stack current"
    elif capture_recovery < 0.93:
        bottleneck = "Front-end lithium capture"
    else:
        bottleneck = "Feed throughput / chemistry"

    impurity_tolerance_score = clamp(
        100.0 - impurity_severity * 5.5 + polish_efficiency * 0.22,
        10.0,
        100.0,
    )

    return {
        "route_name": route_name,
        "li_feed_kg_h": li_feed_kg_h,
        "li_feed_mol_h": li_feed_mol_h,
        "li_captured_kg_h": li_captured_kg_h,
        "li_converted_kg_h": li_converted_kg_h,
        "lioh_kg_h": lioh_kg_h,
        "lioh_tpy": lioh_tpy,
        "cash_cost_ton": cash_cost_ton,
        "power_kw": power_kw,
        "annual_energy_mwh": annual_energy_mwh,
        "specific_energy_kwh_kg": specific_energy_kwh_kg,
        "power_cost_ton": power_cost_ton,
        "route_adjusted_reagent_cost": route_adjusted_reagent_cost,
        "purity_proxy": purity_proxy,
        "impurity_tolerance_score": impurity_tolerance_score,
        "utilization_pct": utilization_pct,
        "bottleneck": bottleneck,
        "impurity_severity": impurity_severity,
        "chloride_equivalent_gl": chloride_equivalent_gl,
        "sulfate_equivalent_gl": sulfate_equivalent_gl,
        "required_area_m2": required_area_m2,
        "provided_area_m2": provided_area_m2,
        "conversion_adjusted": conversion_adjusted,
        "effective_crystallization_yield": effective_crystallization_yield,
        "installed_current_a": installed_current_a,
        "capture_recovery_pct": capture_recovery * 100.0,
        "area_constraint": area_constraint,
        "annualized_capex": annualized_capex,
        "opex_ton": opex_ton,
    }
