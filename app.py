import io
import math
import pandas as pd
import streamlit as st
import altair as alt

from model import run_model
from config import OPERATING_WINDOWS, FEEDSTOCK_PRESETS


st.set_page_config(page_title="MONOLiTH Pilot Plant Simulator", layout="wide")


# -----------------------------
# STATUS HELPERS
# -----------------------------

def classify_status(value, config):
    if config["green_min"] <= value <= config["green_max"]:
        return "Green", "🟢", config["green_msg"]
    if config["yellow_min"] <= value <= config["yellow_max"]:
        return "Yellow", "🟡", config["yellow_msg"]
    return "Red", "🔴", config["red_msg"]


def build_status_item(key, value):
    cfg = OPERATING_WINDOWS[key]
    level, icon, message = classify_status(value, cfg)
    return {
        "Parameter": cfg["label"],
        "Value": f"{value:.2f} {cfg['units']}" if isinstance(value, float) else f"{value} {cfg['units']}",
        "Status": f"{icon} {level}",
        "Meaning": message,
        "Level": level,
    }


def render_status_box(item):
    if item["Level"] == "Green":
        st.success(f"{item['Parameter']}: {item['Status']} — {item['Meaning']}")
    elif item["Level"] == "Yellow":
        st.warning(f"{item['Parameter']}: {item['Status']} — {item['Meaning']}")
    else:
        st.error(f"{item['Parameter']}: {item['Status']} — {item['Meaning']}")


def health_score_from_statuses(status_items):
    weights = {"Green": 100, "Yellow": 65, "Red": 25}
    return sum(weights[item["Level"]] for item in status_items) / len(status_items)


def health_label(score):
    if score >= 85:
        return "🟢 Healthy operating window"
    if score >= 60:
        return "🟡 Caution / economically stressed"
    return "🔴 Outside preferred operating window"


# -----------------------------
# PROCESS FLOW HELPERS
# -----------------------------

def unit_level_from_status_items(status_items):
    if any(item["Level"] == "Red" for item in status_items):
        return "Red"
    if any(item["Level"] == "Yellow" for item in status_items):
        return "Yellow"
    return "Green"


def bottleneck_unit_map(bottleneck_text):
    if bottleneck_text == "Front-end lithium capture":
        return "Capture"
    if bottleneck_text == "Installed stack current":
        return "Electrochemical Stack"
    if bottleneck_text == "Membrane area / stack geometry":
        return "Electrochemical Stack"
    if bottleneck_text == "Feed throughput / chemistry":
        return "Feed"
    return None


def unit_style(level, is_bottleneck=False):
    if level == "Green":
        style = {
            "border": "#22c55e",
            "bg": "#0f172a",
            "text": "#e5e7eb",
            "accent": "🟢",
        }
    elif level == "Yellow":
        style = {
            "border": "#eab308",
            "bg": "#0f172a",
            "text": "#e5e7eb",
            "accent": "🟡",
        }
    else:
        style = {
            "border": "#ef4444",
            "bg": "#0f172a",
            "text": "#e5e7eb",
            "accent": "🔴",
        }

    if is_bottleneck:
        style["border"] = "#f97316"
        style["accent"] = "🚧"
        style["shadow"] = "0 0 0 3px rgba(249,115,22,0.30), 0 6px 18px rgba(0,0,0,0.22)"
    else:
        style["shadow"] = "0 4px 14px rgba(0,0,0,0.18)"

    return style


def render_unit_card(title, lines, level, is_bottleneck=False):
    style = unit_style(level, is_bottleneck=is_bottleneck)
    body = "<br>".join(lines)

    bottleneck_tag = ""
    if is_bottleneck:
        bottleneck_tag = (
            '<div style="font-size:11px; font-weight:700; color:#fdba74; '
            'margin-bottom:6px;">LIMITING UNIT</div>'
        )

    html = (
        f'<div style="'
        f'background:{style["bg"]};'
        f'color:{style["text"]};'
        f'border:2px solid {style["border"]};'
        f'border-radius:18px;'
        f'padding:16px 14px;'
        f'text-align:center;'
        f'min-height:162px;'
        f'display:flex;'
        f'flex-direction:column;'
        f'justify-content:center;'
        f'box-shadow:{style["shadow"]};'
        f'">'
        f'<div style="font-size:24px; margin-bottom:6px;">{style["accent"]}</div>'
        f'{bottleneck_tag}'
        f'<div style="font-size:15px; font-weight:700; margin-bottom:8px;">{title}</div>'
        f'<div style="font-size:13px; line-height:1.45;">{body}</div>'
        f'</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def render_arrow():
    st.markdown(
        """
        <div style="
            height:162px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:34px;
            color:#94a3b8;
            font-weight:700;
        ">
            →
        </div>
        """,
        unsafe_allow_html=True,
    )


def scale_capex(base_capex_m, scaling_factor, exponent=0.65):
    return base_capex_m * (scaling_factor ** exponent)


def load_fraction_from_power_price(price):
    if price <= 20:
        return 1.00
    if price <= 40:
        return 0.85
    if price <= 60:
        return 0.65
    if price <= 80:
        return 0.40
    return 0.20


# -----------------------------
# UI HEADER
# -----------------------------

st.title("MONOLiTH Pilot Plant Simulator")

st.write(
    "Pilot-scale lithium hydroxide model with feed chemistry, electrochemical "
    "stack sizing, energy, economics, operating window monitoring, scenario "
    "comparison, charts, a live process ribbon, plant capacity scaling, "
    "investor-style metrics, and power flexibility mode."
)

st.info(
    "Use this simulator from top to bottom. Start with a feedstock preset, then set "
    "target plant capacity, then refine chemistry, recovery, stack, and economics. "
    "The dashboard updates live and highlights plant health, bottlenecks, production, "
    "cost, and flexible power behavior."
)

with st.expander("How to use this simulator"):
    st.markdown(
        """
        **Recommended workflow**

        1. **Choose a feedstock preset**  
        Start with a representative brine or Li salt stream to populate the chemistry.

        2. **Set target plant capacity**  
        This scales feed flow, suggested stack count, and CAPEX basis.

        3. **Review feed chemistry**  
        Adjust lithium concentration and impurity levels such as Mg, Ca, sulfate, and boron.

        4. **Tune capture and polishing**  
        These govern front-end lithium recovery and impurity cleanup before the electrochemical step.

        5. **Tune electrochemical stack assumptions**  
        Current density, Faradaic efficiency, current per stack, and stack count control throughput and energy use.

        6. **Review crystallization and purity**  
        Crystallizer yield and mother liquor recovery affect final product output and quality.

        7. **Review economics**  
        Power price, reagent cost, labor, CAPEX, selling price, and overhead shape the commercial picture.

        8. **Use the diagnostics**  
        - **Plant Health Monitor** shows whether the process is in a favorable operating window  
        - **Live Process Flow Diagram** shows where the process is constrained  
        - **Scenario Comparison** compares process routes or stressed cases  
        - **Power Flexibility Mode** shows how the plant performs under changing electricity prices

        **Important note**  
        This is a first-pass engineering and techno-economic simulator. It is useful for scenario testing,
        early design logic, and investor storytelling, but it is not yet a full first-principles process model.
        """
    )

with st.expander("Definitions and modeling notes"):
    st.markdown(
        """
        **CAPEX scaling exponent**  
        The exponent used in the common process-scaling relationship:  
        **CAPEX ∝ capacity^n**.  
        A value around **0.6 to 0.7** is often used for early industrial scaling. Lower values imply stronger economies of scale.

        **Minimum turndown fraction**  
        The lowest fraction of full plant load that the system is allowed to run at during flexible operation.  
        Example: **0.20 = 20% of full load**.

        **Faradaic efficiency**  
        The fraction of electrical current that actually drives the desired lithium conversion chemistry instead of side reactions.

        **Current density**  
        Electrical current per membrane/electrode area. Higher current density usually increases throughput, but can also increase stress, overpotential, and efficiency loss.

        **Current per stack**  
        Total current sent through one electrochemical stack. Together with stack count, this determines installed electrochemical capacity.

        **Conversion per pass**  
        Fraction of lithium converted in a single pass through the electrochemical system.

        **Recycle ratio**  
        Amount of internal recycle relative to forward flow. Higher recycle can improve effective conversion, but may increase circulation burden.

        **Polishing efficiency**  
        A simplified measure of how well the purification train removes or suppresses impurity impacts before electrochemical conversion.

        **Crystallizer yield**  
        Fraction of dissolved product recovered in the crystallization step before mother liquor recovery effects are added.

        **Mother liquor recovery**  
        Fraction of remaining dissolved product recovered from the mother liquor loop.

        **Specific energy (kWh/kg)**  
        Electrical energy consumed per kilogram of LiOH·H₂O product.

        **CAPEX intensity ($/t capacity)**  
        Installed CAPEX divided by target annual production capacity.

        **EBITDA proxy**  
        A first-pass estimate of earnings before interest, taxes, depreciation, and amortization, using the simplified commercial assumptions in this model.

        **Simple payback**  
        Installed CAPEX divided by EBITDA proxy. This is only a rough screening metric, not a full project-finance result.
        """
    )


# -----------------------------
# FEEDSTOCK PRESET
# -----------------------------

preset_name = st.selectbox(
    "Feedstock Source",
    list(FEEDSTOCK_PRESETS.keys()),
    index=0,
    help="Select a representative feed chemistry preset. You can still manually override the values after selection.",
)

preset = FEEDSTOCK_PRESETS[preset_name]


# -----------------------------
# PLANT CAPACITY
# -----------------------------

st.header("Plant Capacity")

col1, col2, col3 = st.columns(3)

with col1:
    target_capacity_tpy = st.slider(
        "Target LiOH·H₂O production (t/y)",
        250,
        50000,
        2000,
        250,
        help="Target annual lithium hydroxide monohydrate production capacity used for top-level plant scaling.",
    )

with col2:
    reference_capacity_tpy = st.number_input(
        "Reference plant size for scaling (t/y)",
        min_value=100,
        max_value=50000,
        value=2000,
        step=100,
        help="Reference plant basis used to calculate the capacity scaling factor.",
    )

with col3:
    capex_scaling_exponent = st.slider(
        "CAPEX scaling exponent",
        0.50,
        0.90,
        0.65,
        0.01,
        help="Exponent in the scaling rule CAPEX ∝ capacity^n. Lower values imply stronger economies of scale.",
    )

capacity_scale_factor = target_capacity_tpy / reference_capacity_tpy

st.caption(
    f"Capacity scaling factor = {capacity_scale_factor:.2f}× relative to "
    f"{reference_capacity_tpy:,} t/y reference."
)


# -----------------------------
# PROCESS ROUTE
# -----------------------------

st.header("Process Route")

feed_mode = st.selectbox(
    "Feed chemistry",
    ["LiCl", "Li2SO4"],
    index=0 if preset["feed_mode"] == "LiCl" else 1,
    help="Choose the lithium salt basis for the process route. This affects route-specific penalties and assumptions in the model.",
)


# -----------------------------
# FEED CONDITIONS
# -----------------------------

st.header("Feed Conditions")

scaled_flow_default = max(1.0, float(preset["flow_m3h"]) * capacity_scale_factor)

col1, col2, col3 = st.columns(3)

with col1:
    flow_m3h = st.slider(
        "Feed flow rate (m³/h)",
        1.0,
        1500.0,
        min(scaled_flow_default, 1500.0),
        1.0,
        help="Volumetric feed rate into the plant. Capacity scaling pushes this higher or lower based on the selected plant size.",
    )
    li_conc = st.slider(
        "Lithium concentration (g/L)",
        0.1,
        6.0,
        float(preset["li_conc"]),
        0.1,
        help="Lithium concentration in the incoming stream.",
    )
    uptime = st.slider(
        "Plant uptime (%)",
        60.0,
        100.0,
        92.0,
        1.0,
        help="Fraction of the year the plant is online and operating.",
    )

with col2:
    mg_gl = st.slider(
        "Mg concentration (g/L)",
        0.0,
        5.0,
        float(preset["mg_gl"]),
        0.05,
        help="Magnesium is a high-impact divalent impurity that can strongly increase purification burden.",
    )
    ca_gl = st.slider(
        "Ca concentration (g/L)",
        0.0,
        5.0,
        float(preset["ca_gl"]),
        0.05,
        help="Calcium is another divalent impurity that can increase front-end cleanup demands.",
    )
    na_gl = st.slider(
        "Na concentration (g/L)",
        0.0,
        40.0,
        float(preset["na_gl"]),
        0.5,
        help="Sodium contributes to the overall alkali burden in the feed.",
    )

with col3:
    k_gl = st.slider(
        "K concentration (g/L)",
        0.0,
        20.0,
        float(preset["k_gl"]),
        0.2,
        help="Potassium contributes to the overall alkali burden in the feed.",
    )
    so4_gl = st.slider(
        "External sulfate concentration (g/L)",
        0.0,
        10.0,
        float(preset["so4_gl"]),
        0.1,
        help="External sulfate burden entering the process. This can penalize polishing and downstream conversion.",
    )
    b_gl = st.slider(
        "Boron concentration (g/L)",
        0.0,
        3.0,
        float(preset["b_gl"]),
        0.05,
        help="Boron is a feed impurity included in the simplified impurity severity index.",
    )


# -----------------------------
# CAPTURE + POLISHING
# -----------------------------

st.header("Capture + Polishing")

col1, col2, col3 = st.columns(3)

with col1:
    li_capture = st.slider(
        "Lithium capture (%)",
        70.0,
        99.0,
        95.0,
        0.5,
        help="Fraction of lithium recovered in the front-end capture step.",
    )

with col2:
    wash_recovery = st.slider(
        "Wash recovery (%)",
        85.0,
        99.5,
        98.0,
        0.5,
        help="Lithium recovery retained during washing or post-capture handling.",
    )

with col3:
    polish_efficiency = st.slider(
        "Polishing efficiency (%)",
        50.0,
        99.0,
        85.0,
        1.0,
        help="Simplified measure of how effectively the polishing train suppresses impurity impact before electrochemical conversion.",
    )


# -----------------------------
# ELECTROCHEMICAL STACK
# -----------------------------

st.header("Electrochemical Stack")

scaled_stack_default = max(1, int(round(12 * capacity_scale_factor)))

col1, col2, col3 = st.columns(3)

with col1:
    faradaic_eff = st.slider(
        "Faradaic efficiency (%)",
        60.0,
        99.0,
        90.0,
        0.5,
        help="Fraction of electrical current that goes to the desired lithium conversion rather than side reactions.",
    )
    current_density = st.slider(
        "Current density (A/m²)",
        50,
        800,
        350,
        10,
        help="Electrical current per active area. Higher values raise throughput but can increase stack stress and efficiency loss.",
    )

with col2:
    cell_voltage = st.slider(
        "Cell voltage (V)",
        2.5,
        6.5,
        4.4,
        0.1,
        help="Average cell voltage used in the electrochemical energy calculation.",
    )
    current_per_stack = st.slider(
        "Current per stack (A)",
        100,
        5000,
        2500,
        50,
        help="Total current assigned to each electrochemical stack.",
    )

with col3:
    active_area_per_stack = st.slider(
        "Active area per stack (m²)",
        0.5,
        25.0,
        8.0,
        0.5,
        help="Effective membrane or electrode area available per stack.",
    )
    stack_count = st.slider(
        "Number of stacks",
        1,
        500,
        min(scaled_stack_default, 500),
        1,
        help="Total number of installed electrochemical stacks.",
    )

conversion_per_pass = st.slider(
    "Conversion per pass (%)",
    40.0,
    98.0,
    88.0,
    1.0,
    help="Fraction of lithium converted in one pass through the electrochemical system.",
)

recycle_ratio = st.slider(
    "Recycle ratio (x)",
    0.0,
    8.0,
    2.5,
    0.1,
    help="Internal recycle relative to forward flow. Higher recycle can improve effective conversion but increases circulation burden.",
)


# -----------------------------
# CRYSTALLIZATION
# -----------------------------

st.header("Crystallization + Product")

col1, col2, col3 = st.columns(3)

with col1:
    crystallizer_yield = st.slider(
        "Crystallizer yield (%)",
        70.0,
        99.0,
        94.0,
        0.5,
        help="Primary yield from the crystallization step before mother liquor recovery is added.",
    )

with col2:
    mother_liquor_recovery = st.slider(
        "Mother liquor recovery (%)",
        0.0,
        95.0,
        60.0,
        1.0,
        help="Additional product recovery from the mother liquor loop.",
    )

with col3:
    target_purity = st.slider(
        "Target purity (wt%)",
        98.0,
        99.9,
        99.5,
        0.1,
        help="Target product purity used in the purity proxy calculation.",
    )


# -----------------------------
# ECONOMICS
# -----------------------------

st.header("Economics")

scaled_capex_default = scale_capex(24.0, capacity_scale_factor, capex_scaling_exponent)

col1, col2, col3, col4 = st.columns(4)

with col1:
    power_price = st.slider(
        "Power price ($/MWh)",
        10.0,
        150.0,
        45.0,
        1.0,
        help="Electricity price used for the baseline energy-cost calculation.",
    )
    reagent_cost_ton = st.slider(
        "Base reagent cost ($/t product)",
        0.0,
        2000.0,
        280.0,
        10.0,
        help="Baseline reagent cost per ton of LiOH·H₂O product before route adjustments.",
    )

with col2:
    labor_maint_ton = st.slider(
        "Labor + maintenance ($/t product)",
        100.0,
        3000.0,
        640.0,
        25.0,
        help="Combined labor and maintenance burden per ton of product.",
    )
    capex_m = st.slider(
        "Installed CAPEX ($M)",
        1.0,
        500.0,
        min(scaled_capex_default, 500.0),
        1.0,
        help="Installed capital cost for the plant.",
    )

with col3:
    project_years = st.slider(
        "Project life (years)",
        5,
        25,
        15,
        1,
        help="Project life used for annualized CAPEX and simplified economics.",
    )
    selling_price_ton = st.slider(
        "LiOH selling price ($/t)",
        4000.0,
        30000.0,
        12000.0,
        250.0,
        help="Assumed realized selling price for lithium hydroxide monohydrate used in revenue and EBITDA proxy calculations.",
    )

with col4:
    corporate_overhead_m = st.slider(
        "Corporate / SG&A ($M/y)",
        0.0,
        50.0,
        2.0,
        0.5,
        help="Annual corporate overhead, general and administrative cost, or non-plant operating burden.",
    )
    sustaining_capex_pct = st.slider(
        "Sustaining CAPEX (% of installed CAPEX / y)",
        0.0,
        10.0,
        2.0,
        0.5,
        help="Annual sustaining capital as a percent of installed CAPEX.",
    )


# -----------------------------
# RUN MODEL
# -----------------------------

inputs = {
    "feed_mode": feed_mode,
    "flow_m3h": flow_m3h,
    "li_conc": li_conc,
    "uptime": uptime,
    "mg_gl": mg_gl,
    "ca_gl": ca_gl,
    "na_gl": na_gl,
    "k_gl": k_gl,
    "so4_gl": so4_gl,
    "b_gl": b_gl,
    "li_capture": li_capture,
    "wash_recovery": wash_recovery,
    "polish_efficiency": polish_efficiency,
    "faradaic_eff": faradaic_eff,
    "current_density": current_density,
    "cell_voltage": cell_voltage,
    "current_per_stack": current_per_stack,
    "active_area_per_stack": active_area_per_stack,
    "stack_count": stack_count,
    "conversion_per_pass": conversion_per_pass,
    "recycle_ratio": recycle_ratio,
    "crystallizer_yield": crystallizer_yield,
    "mother_liquor_recovery": mother_liquor_recovery,
    "target_purity": target_purity,
    "power_price": power_price,
    "reagent_cost_ton": reagent_cost_ton,
    "labor_maint_ton": labor_maint_ton,
    "capex_m": capex_m,
    "project_years": project_years,
}

results = run_model(inputs)

st.caption(
    f"Current basis: {results['route_name']} • Preset: {preset_name} • "
    f"Target capacity: {target_capacity_tpy:,} t/y"
)


# -----------------------------
# INVESTOR METRICS
# -----------------------------

annual_revenue = results["lioh_tpy"] * selling_price_ton
annual_gross_profit = results["lioh_tpy"] * (selling_price_ton - results["cash_cost_ton"])
annual_sustaining_capex = capex_m * 1_000_000.0 * (sustaining_capex_pct / 100.0)
annual_ebitda_proxy = annual_gross_profit - (corporate_overhead_m * 1_000_000.0) - annual_sustaining_capex
ebitda_margin_pct = (annual_ebitda_proxy / annual_revenue * 100.0) if annual_revenue > 0 else 0.0
capex_intensity = (capex_m * 1_000_000.0) / max(target_capacity_tpy, 1.0)
simple_payback_years = (capex_m * 1_000_000.0) / annual_ebitda_proxy if annual_ebitda_proxy > 0 else None
gross_margin_ton = selling_price_ton - results["cash_cost_ton"]

st.header("Investor Metrics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue Proxy", f"${annual_revenue/1_000_000:,.1f}M/y")
col2.metric("EBITDA Proxy", f"${annual_ebitda_proxy/1_000_000:,.1f}M/y")
col3.metric("EBITDA Margin", f"{ebitda_margin_pct:,.1f}%")
col4.metric("CAPEX Intensity", f"${capex_intensity:,.0f}/t cap.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Gross Margin / t", f"${gross_margin_ton:,.0f}/t")
col2.metric("Corporate Overhead", f"${corporate_overhead_m:,.1f}M/y")
col3.metric("Sustaining CAPEX", f"${annual_sustaining_capex/1_000_000:,.1f}M/y")
if simple_payback_years is None:
    col4.metric("Simple Payback", "N/A")
else:
    col4.metric("Simple Payback", f"{simple_payback_years:,.1f} y")


# -----------------------------
# POWER FLEXIBILITY MODE
# -----------------------------

st.header("Power Flexibility Mode")

col1, col2 = st.columns(2)

with col1:
    flexibility_mode = st.toggle(
        "Enable load-following power mode",
        value=True,
        help="If enabled, plant load follows electricity price using a simplified dispatch rule.",
    )

with col2:
    min_load_fraction = st.slider(
        "Minimum turndown fraction",
        0.10,
        1.00,
        0.20,
        0.05,
        help="Lowest fraction of full plant load allowed during flexible operation. Example: 0.20 means the plant can turn down to 20% load.",
    )

power_flex_rows = []
for price in [20.0, 40.0, 60.0, 80.0, 100.0]:
    base_load = load_fraction_from_power_price(price)
    load_fraction = max(min_load_fraction, base_load) if flexibility_mode else 1.0

    flex_revenue = annual_revenue * load_fraction
    flex_ebitda = (
        annual_revenue * load_fraction
        - (results["cash_cost_ton"] * results["lioh_tpy"] * load_fraction)
        - (corporate_overhead_m * 1_000_000.0)
        - annual_sustaining_capex
    )

    flex_lioh = results["lioh_tpy"] * load_fraction
    flex_power = results["power_kw"] * load_fraction

    power_flex_rows.append(
        {
            "PowerPrice_$per_MWh": price,
            "LoadFraction_pct": load_fraction * 100.0,
            "LiOH_tpy": flex_lioh,
            "Power_kW": flex_power,
            "Revenue_$per_y": flex_revenue,
            "EBITDA_$per_y": flex_ebitda,
        }
    )

power_flex_df = pd.DataFrame(power_flex_rows)
st.dataframe(power_flex_df, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    load_chart = (
        alt.Chart(power_flex_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("PowerPrice_$per_MWh:Q", title="Power price ($/MWh)"),
            y=alt.Y("LoadFraction_pct:Q", title="Plant load (%)"),
            tooltip=["PowerPrice_$per_MWh", "LoadFraction_pct"],
        )
        .properties(title="Load-following operation", height=300)
    )
    st.altair_chart(load_chart, use_container_width=True)

with col2:
    ebitda_flex_chart = (
        alt.Chart(power_flex_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("PowerPrice_$per_MWh:Q", title="Power price ($/MWh)"),
            y=alt.Y("EBITDA_$per_y:Q", title="EBITDA proxy ($/y)"),
            tooltip=["PowerPrice_$per_MWh", "EBITDA_$per_y"],
        )
        .properties(title="EBITDA under flexible load", height=300)
    )
    st.altair_chart(ebitda_flex_chart, use_container_width=True)


# -----------------------------
# CAPACITY SCALING SUMMARY
# -----------------------------

st.header("Capacity Scaling Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Target Capacity", f"{target_capacity_tpy:,} t/y")
col2.metric("Flow Scale Factor", f"{capacity_scale_factor:.2f}×")
col3.metric("Suggested Stack Count", f"{scaled_stack_default:,}")
col4.metric("Scaled CAPEX Basis", f"${scaled_capex_default:,.1f}M")


# -----------------------------
# LIVE PROCESS FLOW
# -----------------------------

st.header("Live Process Flow Diagram")

feed_status = [
    build_status_item("mg_gl", mg_gl),
    build_status_item("so4_gl", so4_gl),
]

capture_status = [
    build_status_item("li_capture", li_capture),
]

polishing_status = [
    build_status_item("polish_efficiency", polish_efficiency),
]

stack_status = [
    build_status_item("current_density", current_density),
    build_status_item("faradaic_eff", faradaic_eff),
    build_status_item("specific_energy_kwh_kg", results["specific_energy_kwh_kg"]),
]

crystallizer_status = [
    build_status_item("cash_cost_ton", results["cash_cost_ton"]),
]

product_status = [
    build_status_item("cash_cost_ton", results["cash_cost_ton"]),
]

feed_level = unit_level_from_status_items(feed_status)
capture_level = unit_level_from_status_items(capture_status)
polishing_level = unit_level_from_status_items(polishing_status)
stack_level = unit_level_from_status_items(stack_status)
crystallizer_level = unit_level_from_status_items(crystallizer_status)
product_level = unit_level_from_status_items(product_status)

limiting_unit = bottleneck_unit_map(results["bottleneck"])

cols = st.columns([1.35, 0.22, 1.35, 0.22, 1.55, 0.22, 1.8, 0.22, 1.45, 0.22, 1.7])

with cols[0]:
    render_unit_card(
        "Feed",
        [
            f"{feed_mode}",
            f"{flow_m3h:.1f} m³/h",
            f"{results['li_feed_kg_h']:.2f} kg Li/h",
        ],
        feed_level,
        is_bottleneck=(limiting_unit == "Feed"),
    )

with cols[1]:
    render_arrow()

with cols[2]:
    render_unit_card(
        "Capture",
        [
            f"{results['li_captured_kg_h']:.2f} kg Li/h",
            f"{li_capture:.1f}% capture",
            f"{wash_recovery:.1f}% wash",
        ],
        capture_level,
        is_bottleneck=(limiting_unit == "Capture"),
    )

with cols[3]:
    render_arrow()

with cols[4]:
    render_unit_card(
        "Polishing",
        [
            f"Impurity index {results['impurity_severity']:.2f}",
            f"{polish_efficiency:.1f}% polishing",
            f"Mg {mg_gl:.2f} g/L",
        ],
        polishing_level,
        is_bottleneck=(limiting_unit == "Polishing"),
    )

with cols[5]:
    render_arrow()

with cols[6]:
    render_unit_card(
        "Electrochemical Stack",
        [
            f"{results['li_converted_kg_h']:.2f} kg Li/h converted",
            f"{results['power_kw']:,.0f} kW",
            f"{current_density} A/m²",
        ],
        stack_level,
        is_bottleneck=(limiting_unit == "Electrochemical Stack"),
    )

with cols[7]:
    render_arrow()

with cols[8]:
    render_unit_card(
        "Crystallizer",
        [
            f"Purity {results['purity_proxy']:.2f} wt%",
            f"{crystallizer_yield:.1f}% yield",
            f"{mother_liquor_recovery:.1f}% ML recovery",
        ],
        crystallizer_level,
        is_bottleneck=(limiting_unit == "Crystallizer"),
    )

with cols[9]:
    render_arrow()

with cols[10]:
    render_unit_card(
        "LiOH·H₂O Product",
        [
            f"{results['lioh_kg_h']:.2f} kg/h",
            f"{results['lioh_tpy']:,.0f} t/y",
            f"${results['cash_cost_ton']:,.0f}/t",
        ],
        product_level,
        is_bottleneck=False,
    )

if limiting_unit:
    st.warning(f"Current limiting unit: **{limiting_unit}**")


# -----------------------------
# HEALTH MONITOR
# -----------------------------

st.header("Plant Health Monitor")

status_items = [
    build_status_item("current_density", current_density),
    build_status_item("faradaic_eff", faradaic_eff),
    build_status_item("mg_gl", mg_gl),
    build_status_item("so4_gl", so4_gl),
    build_status_item("power_price", power_price),
    build_status_item("polish_efficiency", polish_efficiency),
    build_status_item("li_capture", li_capture),
    build_status_item("specific_energy_kwh_kg", results["specific_energy_kwh_kg"]),
    build_status_item("cash_cost_ton", results["cash_cost_ton"]),
]

health_score = health_score_from_statuses(status_items)

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("Plant Health Score", f"{health_score:.0f}/100")
    label = health_label(health_score)
    if health_score >= 85:
        st.success(label)
    elif health_score >= 60:
        st.warning(label)
    else:
        st.error(label)

with col2:
    red = sum(item["Level"] == "Red" for item in status_items)
    yellow = sum(item["Level"] == "Yellow" for item in status_items)
    green = sum(item["Level"] == "Green" for item in status_items)

    st.write("**Risk Summary**")
    st.write(f"Green: **{green}**")
    st.write(f"Yellow: **{yellow}**")
    st.write(f"Red: **{red}**")
    st.write(f"Bottleneck: **{results['bottleneck']}**")


# -----------------------------
# OPERATING WINDOW DETAIL
# -----------------------------

st.header("Operating Window Detail")

col1, col2 = st.columns(2)

with col1:
    for item in status_items[:5]:
        render_status_box(item)

with col2:
    for item in status_items[5:]:
        render_status_box(item)


# -----------------------------
# RESULTS
# -----------------------------

st.header("Key Results")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Li Feed", f"{results['li_feed_kg_h']:.2f} kg/h")
col2.metric("Li Captured", f"{results['li_captured_kg_h']:.2f} kg/h")
col3.metric("LiOH Output", f"{results['lioh_tpy']:,.0f} t/y")
col4.metric("Cash Cost", f"${results['cash_cost_ton']:,.0f}/t")


# -----------------------------
# SCENARIO COMPARISON
# -----------------------------

st.header("Scenario Comparison")

scenario_mode = st.radio(
    "Comparison mode",
    ["Route comparison", "Base vs stressed case"],
    horizontal=True,
)

base_inputs = inputs.copy()

if scenario_mode == "Route comparison":
    scenario_a = base_inputs.copy()
    scenario_b = base_inputs.copy()
    scenario_a["feed_mode"] = "LiCl"
    scenario_b["feed_mode"] = "Li2SO4"
    label_a = "LiCl"
    label_b = "Li2SO4"
else:
    scenario_a = base_inputs.copy()
    scenario_b = base_inputs.copy()
    scenario_b["mg_gl"] = min(base_inputs["mg_gl"] * 2.0 + 0.1, 5.0)
    scenario_b["ca_gl"] = min(base_inputs["ca_gl"] * 2.0 + 0.1, 5.0)
    scenario_b["so4_gl"] = min(base_inputs["so4_gl"] * 1.5 + 0.5, 10.0)
    scenario_b["li_capture"] = max(base_inputs["li_capture"] - 3.0, 70.0)
    scenario_b["polish_efficiency"] = max(base_inputs["polish_efficiency"] - 5.0, 50.0)
    scenario_b["faradaic_eff"] = max(base_inputs["faradaic_eff"] - 4.0, 60.0)
    scenario_b["power_price"] = min(base_inputs["power_price"] + 20.0, 150.0)
    label_a = "Base case"
    label_b = "Stressed case"

res_a = run_model(scenario_a)
res_b = run_model(scenario_b)

comparison_df = pd.DataFrame(
    [
        {
            "Scenario": label_a,
            "Route": res_a["route_name"],
            "LiOH_tpy": res_a["lioh_tpy"],
            "CashCost_$per_t": res_a["cash_cost_ton"],
            "SpecificEnergy_kWh_per_kg": res_a["specific_energy_kwh_kg"],
            "Purity_wt_pct": res_a["purity_proxy"],
            "Power_kW": res_a["power_kw"],
            "CaptureRecovery_pct": res_a["capture_recovery_pct"],
            "ImpuritySeverity": res_a["impurity_severity"],
            "Utilization_pct": res_a["utilization_pct"],
            "Bottleneck": res_a["bottleneck"],
        },
        {
            "Scenario": label_b,
            "Route": res_b["route_name"],
            "LiOH_tpy": res_b["lioh_tpy"],
            "CashCost_$per_t": res_b["cash_cost_ton"],
            "SpecificEnergy_kWh_per_kg": res_b["specific_energy_kwh_kg"],
            "Purity_wt_pct": res_b["purity_proxy"],
            "Power_kW": res_b["power_kw"],
            "CaptureRecovery_pct": res_b["capture_recovery_pct"],
            "ImpuritySeverity": res_b["impurity_severity"],
            "Utilization_pct": res_b["utilization_pct"],
            "Bottleneck": res_b["bottleneck"],
        },
    ]
)

st.dataframe(comparison_df, use_container_width=True)

csv_buffer = io.StringIO()
comparison_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download scenario comparison CSV",
    data=csv_buffer.getvalue(),
    file_name="monolith_scenario_comparison.csv",
    mime="text/csv",
)


# -----------------------------
# QUICK SENSITIVITY
# -----------------------------

st.header("Quick Sensitivity")

sensitivity_metric = st.selectbox(
    "Sensitivity metric",
    ["LiOH_tpy", "CashCost_$per_t", "SpecificEnergy_kWh_per_kg"],
)

power_range = [20.0, 40.0, 60.0, 80.0, 100.0]
sens_rows = []

for price in power_range:
    sens_inputs = base_inputs.copy()
    sens_inputs["power_price"] = price
    sens_results = run_model(sens_inputs)
    sens_rows.append(
        {
            "PowerPrice_$per_MWh": price,
            "LiOH_tpy": sens_results["lioh_tpy"],
            "CashCost_$per_t": sens_results["cash_cost_ton"],
            "SpecificEnergy_kWh_per_kg": sens_results["specific_energy_kwh_kg"],
        }
    )

sensitivity_df = pd.DataFrame(sens_rows)
st.dataframe(sensitivity_df, use_container_width=True)


# -----------------------------
# CHARTS
# -----------------------------

st.header("Charts")

metric_options = {
    "LiOH output (t/y)": "LiOH_tpy",
    "Cash cost ($/t)": "CashCost_$per_t",
    "Specific energy (kWh/kg)": "SpecificEnergy_kWh_per_kg",
    "Purity proxy (wt%)": "Purity_wt_pct",
    "Power draw (kW)": "Power_kW",
    "Capture recovery (%)": "CaptureRecovery_pct",
    "Utilization (%)": "Utilization_pct",
    "EBITDA proxy ($/y)": "EBITDA_$per_y",
}

chart_df = comparison_df.copy()
chart_df["EBITDA_$per_y"] = [
    (res_a["lioh_tpy"] * (selling_price_ton - res_a["cash_cost_ton"])) - (corporate_overhead_m * 1_000_000.0) - annual_sustaining_capex,
    (res_b["lioh_tpy"] * (selling_price_ton - res_b["cash_cost_ton"])) - (corporate_overhead_m * 1_000_000.0) - annual_sustaining_capex,
]

selected_metric = st.selectbox("Chart metric", list(metric_options.keys()))

metric_col = metric_options[selected_metric]

col1, col2 = st.columns(2)

with col1:
    scenario_chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("Scenario:N", title="Scenario"),
            y=alt.Y(f"{metric_col}:Q", title=selected_metric),
            tooltip=["Scenario", "Route", metric_col],
        )
        .properties(title="Scenario Comparison", height=300)
    )
    st.altair_chart(scenario_chart, use_container_width=True)

with col2:
    sensitivity_chart = (
        alt.Chart(sensitivity_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("PowerPrice_$per_MWh:Q", title="Power price ($/MWh)"),
            y=alt.Y(f"{sensitivity_metric}:Q", title=sensitivity_metric),
            tooltip=["PowerPrice_$per_MWh", sensitivity_metric],
        )
        .properties(title="Power Sensitivity", height=300)
    )
    st.altair_chart(sensitivity_chart, use_container_width=True)
