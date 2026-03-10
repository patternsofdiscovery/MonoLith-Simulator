import io
import math
import pandas as pd
import streamlit as st
import altair as alt

from model import run_model
from config import OPERATING_WINDOWS, FEEDSTOCK_PRESETS


st.set_page_config(page_title="MONOLiTH Control Room", layout="wide")


# -----------------------------
# PAGE STYLE
# -----------------------------
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1.1rem;
        padding-bottom: 2.0rem;
        max-width: 1600px;
    }

    .control-room-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }

    .control-room-subtitle {
        color: #cbd5e1;
        font-size: 1rem;
        margin-bottom: 0.35rem;
    }

    .control-room-caption {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-bottom: 1rem;
    }

    .top-kpi-card {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        border: 1px solid #1f2937;
        border-radius: 18px;
        padding: 14px 16px;
        min-height: 118px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.18);
    }

    .top-kpi-label {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .top-kpi-value {
        color: #f8fafc;
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.15;
    }

    .top-kpi-sub {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: 6px;
    }

    .section-shell {
        background: #0b1220;
        border: 1px solid #1e293b;
        border-radius: 20px;
        padding: 16px 18px;
        margin-bottom: 16px;
    }

    .section-title {
        color: #f8fafc;
        font-size: 1.08rem;
        font-weight: 800;
        margin-bottom: 0.8rem;
    }

    .alert-card {
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
        border: 1px solid #1f2937;
        background: #111827;
    }

    .alert-red {
        border-left: 5px solid #ef4444;
    }

    .alert-yellow {
        border-left: 5px solid #eab308;
    }

    .alert-green {
        border-left: 5px solid #22c55e;
    }

    .alert-title {
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 4px;
        font-size: 0.95rem;
    }

    .alert-body {
        color: #cbd5e1;
        font-size: 0.86rem;
        line-height: 1.4;
    }

    .mode-pill {
        display: inline-block;
        padding: 4px 10px;
        background: #172554;
        color: #bfdbfe;
        border: 1px solid #1d4ed8;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 0.7rem;
    }

    .plant-box {
        border-radius: 18px;
        padding: 14px 14px;
        text-align: center;
        min-height: 172px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 6px 18px rgba(0,0,0,0.18);
    }

    .plant-box-title {
        font-size: 0.98rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .plant-box-body {
        font-size: 0.82rem;
        line-height: 1.45;
    }

    .small-kpi {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        border: 1px solid #22304a;
        border-radius: 16px;
        padding: 12px 14px;
        min-height: 96px;
    }

    .small-kpi-label {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .small-kpi-value {
        color: #f8fafc;
        font-size: 1.2rem;
        font-weight: 800;
        line-height: 1.15;
    }

    .small-kpi-sub {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-top: 4px;
    }

    .stack-cell-on {
        background: linear-gradient(180deg, #1d4ed8 0%, #0f172a 100%);
        border: 1px solid #60a5fa;
        border-radius: 10px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #eff6ff;
        font-size: 0.74rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .stack-cell-dim {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #94a3b8;
        font-size: 0.74rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .stack-cell-warn {
        background: linear-gradient(180deg, #7c2d12 0%, #0f172a 100%);
        border: 1px solid #fb923c;
        border-radius: 10px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff7ed;
        font-size: 0.74rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .divider-note {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: -6px;
        margin-bottom: 8px;
    }

    .guardrail-box {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }

    .guardrail-title {
        color: #f8fafc;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .guardrail-body {
        color: #cbd5e1;
        font-size: 0.86rem;
        line-height: 1.4;
    }

    div[data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #1f2937;
        padding: 12px;
        border-radius: 16px;
    }

    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #22c55e, #eab308, #ef4444);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
# SAFE VALUE / GUARDRAIL HELPERS
# -----------------------------
def safe_number(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return float(value)
        return float(value)
    except Exception:
        return default


def clamp(value, low=None, high=None):
    v = value
    if low is not None:
        v = max(low, v)
    if high is not None:
        v = min(high, v)
    return v


def safe_div(numerator, denominator, default=0.0):
    try:
        if denominator is None or abs(denominator) < 1e-12:
            return default
        return numerator / denominator
    except Exception:
        return default


def sanitize_results(raw_results):
    """
    Makes the dashboard more resilient if the model returns odd, missing,
    or slightly unphysical values.
    """
    results = dict(raw_results)

    numeric_keys = [
        "lioh_tpy",
        "cash_cost_ton",
        "specific_energy_kwh_kg",
        "power_kw",
        "purity_proxy",
        "li_feed_kg_h",
        "li_captured_kg_h",
        "li_converted_kg_h",
        "lioh_kg_h",
        "capture_recovery_pct",
        "impurity_severity",
        "utilization_pct",
    ]

    for key in numeric_keys:
        if key in results:
            results[key] = safe_number(results[key], 0.0)

    results["lioh_tpy"] = max(0.0, results.get("lioh_tpy", 0.0))
    results["cash_cost_ton"] = max(0.0, results.get("cash_cost_ton", 0.0))
    results["specific_energy_kwh_kg"] = max(0.0, results.get("specific_energy_kwh_kg", 0.0))
    results["power_kw"] = max(0.0, results.get("power_kw", 0.0))
    results["li_feed_kg_h"] = max(0.0, results.get("li_feed_kg_h", 0.0))
    results["li_captured_kg_h"] = max(0.0, results.get("li_captured_kg_h", 0.0))
    results["li_converted_kg_h"] = max(0.0, results.get("li_converted_kg_h", 0.0))
    results["lioh_kg_h"] = max(0.0, results.get("lioh_kg_h", 0.0))

    results["purity_proxy"] = clamp(results.get("purity_proxy", 0.0), 0.0, 100.0)
    results["capture_recovery_pct"] = clamp(results.get("capture_recovery_pct", 0.0), 0.0, 100.0)
    results["utilization_pct"] = clamp(results.get("utilization_pct", 0.0), 0.0, 100.0)
    results["impurity_severity"] = max(0.0, results.get("impurity_severity", 0.0))

    if "route_name" not in results or not results["route_name"]:
        results["route_name"] = "Unknown route"

    if "bottleneck" not in results or not results["bottleneck"]:
        results["bottleneck"] = "No bottleneck reported"

    return results


def build_guardrail_messages(results, inputs, target_capacity_tpy, selling_price_ton):
    messages = []

    if results["lioh_tpy"] <= 0:
        messages.append(("red", "Zero production output", "The model returned zero LiOH·H₂O output. Review feed chemistry, stack sizing, and recovery assumptions."))

    if results["li_feed_kg_h"] > 0 and results["li_captured_kg_h"] > results["li_feed_kg_h"] * 1.05:
        messages.append(("yellow", "Capture exceeds feed", "Captured lithium is greater than lithium feed by more than 5%. Review recovery logic or model assumptions."))

    if results["li_captured_kg_h"] > 0 and results["li_converted_kg_h"] > results["li_captured_kg_h"] * 1.05:
        messages.append(("yellow", "Conversion exceeds captured lithium", "Converted lithium appears larger than captured lithium. Review electrochemical conversion assumptions."))

    if results["cash_cost_ton"] > selling_price_ton * 1.25 and selling_price_ton > 0:
        messages.append(("red", "Cost exceeds selling price", "Cash cost is materially above the assumed selling price. The commercial case is not currently viable."))

    if results["specific_energy_kwh_kg"] > 50:
        messages.append(("yellow", "Very high specific energy", "Specific energy is above 50 kWh/kg, which may indicate a stressed or unrealistic operating point."))

    if results["purity_proxy"] < 95:
        messages.append(("yellow", "Low product purity", "Purity proxy is below 95 wt%. This may not represent a battery-grade LiOH·H₂O outcome."))

    if results["utilization_pct"] < 10:
        messages.append(("yellow", "Very low utilization", "Stack utilization is extremely low. Review power mode, current density, or installed stack count."))

    if target_capacity_tpy > 0 and results["lioh_tpy"] > target_capacity_tpy * 1.35:
        messages.append(("yellow", "Output materially above target", "Modeled annual output exceeds target capacity by more than 35%. Review sizing assumptions."))

    if inputs["stack_count"] > 0 and results["power_kw"] == 0 and results["lioh_tpy"] > 0:
        messages.append(("yellow", "Zero power with positive output", "The model shows production with zero power draw. Review electrochemical energy assumptions."))

    if not messages:
        messages.append(("green", "No immediate guardrail issues", "The current scenario appears numerically stable and presentation-ready."))

    return messages[:6]


def render_guardrail_box(level, title, body):
    if level == "red":
        st.error(f"**{title}** — {body}")
    elif level == "yellow":
        st.warning(f"**{title}** — {body}")
    else:
        st.success(f"**{title}** — {body}")


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
        return "Electrochemical Stacks"
    if bottleneck_text == "Membrane area / stack geometry":
        return "Electrochemical Stacks"
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
        f'<div class="plant-box" style="'
        f'background:{style["bg"]};'
        f'color:{style["text"]};'
        f'border:2px solid {style["border"]};'
        f'box-shadow:{style["shadow"]};'
        f'">'
        f'<div style="font-size:24px; margin-bottom:6px;">{style["accent"]}</div>'
        f'{bottleneck_tag}'
        f'<div class="plant-box-title">{title}</div>'
        f'<div class="plant-box-body">{body}</div>'
        f'</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def render_arrow():
    st.markdown(
        """
        <div style="
            height:172px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:30px;
            color:#64748b;
            font-weight:800;
        ">→</div>
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
# DIGITAL TWIN HELPERS
# -----------------------------
def render_top_kpi(label, value, subtext):
    st.markdown(
        f"""
        <div class="top-kpi-card">
            <div class="top-kpi-label">{label}</div>
            <div class="top-kpi-value">{value}</div>
            <div class="top-kpi-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_small_kpi(label, value, subtext):
    st.markdown(
        f"""
        <div class="small-kpi">
            <div class="small-kpi-label">{label}</div>
            <div class="small-kpi-value">{value}</div>
            <div class="small-kpi-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_wrapped_value_card(label, value, subtext=""):
    st.markdown(
        f"""
        <div class="small-kpi">
            <div class="small-kpi-label">{label}</div>
            <div style="color:#f8fafc; font-size:1.0rem; font-weight:800; line-height:1.25; white-space:normal; word-break:break-word;">
                {value}
            </div>
            <div class="small-kpi-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert(level, title, body):
    level_class = {
        "red": "alert-red",
        "yellow": "alert-yellow",
        "green": "alert-green",
    }.get(level, "alert-yellow")

    st.markdown(
        f"""
        <div class="alert-card {level_class}">
            <div class="alert-title">{title}</div>
            <div class="alert-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cost_gauge(cost_per_ton, selling_price_ton):
    if selling_price_ton <= 0:
        st.metric("Cost per Ton Gauge", "N/A")
        return

    cost_ratio = safe_div(cost_per_ton, selling_price_ton, default=1.0)

    if cost_ratio <= 0.45:
        gauge_label = "🟢 Strong cost position"
    elif cost_ratio <= 0.70:
        gauge_label = "🟡 Watch cost position"
    else:
        gauge_label = "🔴 Cost structure stressed"

    progress_value = clamp(cost_ratio, 0.0, 1.0)
    st.progress(progress_value)
    st.caption(f"{gauge_label} • Cost = {cost_ratio*100:.1f}% of selling price")


def infer_stack_cells(stack_count, load_fraction, max_display=48):
    actual_active_count = max(1, int(round(stack_count * load_fraction))) if stack_count > 0 else 0
    actual_active_count = min(actual_active_count, stack_count)

    display_count = min(stack_count, max_display)

    if stack_count <= 0:
        displayed_active_count = 0
    else:
        displayed_active_count = int(round(display_count * safe_div(actual_active_count, stack_count, default=0.0)))

    displayed_active_count = min(displayed_active_count, display_count)
    return actual_active_count, display_count, displayed_active_count


def render_stack_farm(stack_count, load_fraction, stressed=False, max_display=48, cols_per_row=8):
    actual_active_count, display_count, displayed_active_count = infer_stack_cells(
        stack_count, load_fraction, max_display=max_display
    )

    for row_start in range(0, display_count, cols_per_row):
        cols = st.columns(cols_per_row)
        for idx in range(cols_per_row):
            cell_num = row_start + idx + 1
            if cell_num > display_count:
                continue

            with cols[idx]:
                if cell_num <= displayed_active_count:
                    klass = "stack-cell-warn" if stressed else "stack-cell-on"
                else:
                    klass = "stack-cell-dim"

                st.markdown(
                    f'<div class="{klass}">S{cell_num}</div>',
                    unsafe_allow_html=True,
                )

    if stack_count > display_count:
        st.caption(
            f"Operator sample view: showing {display_count} representative stacks out of {stack_count} installed. "
            f"Stacks online now: {actual_active_count} / {stack_count}."
        )
    else:
        st.caption(f"Stacks online now: {actual_active_count} / {stack_count}.")


def build_alerts(results, inputs, target_capacity_tpy, selling_price_ton, health_score, flexibility_mode):
    alerts = []

    if inputs["mg_gl"] >= 1.5:
        alerts.append((
            "red",
            "High magnesium burden",
            f"Mg is {inputs['mg_gl']:.2f} g/L. Front-end cleanup demand is elevated and polishing burden is likely increasing cash cost."
        ))
    elif inputs["mg_gl"] >= 0.75:
        alerts.append((
            "yellow",
            "Moderate magnesium burden",
            f"Mg is {inputs['mg_gl']:.2f} g/L. Watch polishing and capture performance."
        ))

    if inputs["so4_gl"] >= 4.0:
        alerts.append((
            "red",
            "High sulfate burden",
            f"Sulfate is {inputs['so4_gl']:.2f} g/L. Route penalties may increase downstream conversion stress and reduce economics."
        ))
    elif inputs["so4_gl"] >= 2.0:
        alerts.append((
            "yellow",
            "Sulfate burden rising",
            f"Sulfate is {inputs['so4_gl']:.2f} g/L. Monitor polishing and route sensitivity."
        ))

    if results["bottleneck"] == "Installed stack current":
        alerts.append((
            "red",
            "Stack-limited throughput",
            "Installed stack current is limiting output. More current per stack or more stacks may be needed."
        ))
    elif results["bottleneck"] == "Membrane area / stack geometry":
        alerts.append((
            "yellow",
            "Membrane area constraint",
            "Electrochemical geometry is constraining performance. Review stack count, active area, or current density."
        ))
    elif results["bottleneck"] == "Front-end lithium capture":
        alerts.append((
            "yellow",
            "Capture-limited throughput",
            "Front-end lithium capture is limiting output. Review capture and wash recovery assumptions."
        ))
    elif results["bottleneck"] == "Feed throughput / chemistry":
        alerts.append((
            "yellow",
            "Feed-limited throughput",
            "Feed rate or chemistry is limiting overall production. Review flow rate and lithium concentration."
        ))

    cost_ratio = safe_div(results["cash_cost_ton"], selling_price_ton, default=999)
    if cost_ratio >= 0.75:
        alerts.append((
            "red",
            "Weak unit margin",
            f"Cash cost is ${results['cash_cost_ton']:,.0f}/t vs ${selling_price_ton:,.0f}/t selling price. Margin is compressed."
        ))
    elif cost_ratio >= 0.55:
        alerts.append((
            "yellow",
            "Margin watch",
            f"Cash cost is ${results['cash_cost_ton']:,.0f}/t. Economics are still workable but should improve."
        ))

    if results["purity_proxy"] < inputs["target_purity"]:
        alerts.append((
            "red",
            "Off-spec purity risk",
            f"Purity proxy is {results['purity_proxy']:.2f} wt% vs target {inputs['target_purity']:.2f} wt%."
        ))

    utilization_gap = target_capacity_tpy - results["lioh_tpy"]
    if utilization_gap > 0.15 * target_capacity_tpy:
        alerts.append((
            "yellow",
            "Below target annual output",
            f"Model output is {results['lioh_tpy']:,.0f} t/y vs target {target_capacity_tpy:,.0f} t/y."
        ))

    if health_score >= 85:
        alerts.append((
            "green",
            "Plant health strong",
            f"Health score is {health_score:.0f}/100. Operating window is favorable."
        ))
    elif health_score < 60:
        alerts.append((
            "red",
            "Plant health stressed",
            f"Health score is {health_score:.0f}/100. Process window is outside preferred conditions."
        ))

    if flexibility_mode:
        alerts.append((
            "green",
            "Load-following enabled",
            "Digital twin is evaluating power-flexible dispatch behavior under variable electricity price."
        ))

    return alerts[:8]


def make_mode_preset(mode_name, preset):
    base = {
        "feed_mode": preset["feed_mode"],
        "target_capacity_tpy": 2000,
        "li_capture": 95.0,
        "wash_recovery": 98.0,
        "polish_efficiency": 85.0,
        "faradaic_eff": 90.0,
        "current_density": 350,
        "cell_voltage": 4.4,
        "current_per_stack": 2500,
        "active_area_per_stack": 8.0,
        "stack_count": 12,
        "conversion_per_pass": 88.0,
        "recycle_ratio": 2.5,
        "crystallizer_yield": 94.0,
        "mother_liquor_recovery": 60.0,
        "target_purity": 99.5,
        "power_price": 45.0,
        "reagent_cost_ton": 280.0,
        "labor_maint_ton": 640.0,
        "selling_price_ton": 12000.0,
        "corporate_overhead_m": 2.0,
        "capex_scaling_exponent": 0.65,
        "min_load_fraction": 0.20,
        "flexibility_mode": True,
        "uptime": 92.0,
    }

    if mode_name == "Low Cost Power":
        base.update({
            "power_price": 22.0,
            "current_density": 420,
            "faradaic_eff": 91.0,
            "stack_count": 14,
        })
    elif mode_name == "Dirty Brine":
        base.update({
            "li_capture": 91.0,
            "polish_efficiency": 76.0,
            "faradaic_eff": 86.0,
            "power_price": 55.0,
        })
    elif mode_name == "High Throughput":
        base.update({
            "target_capacity_tpy": 5000,
            "current_density": 500,
            "current_per_stack": 3200,
            "stack_count": 24,
            "power_price": 40.0,
        })
    elif mode_name == "Investor Case":
        base.update({
            "target_capacity_tpy": 2000,
            "li_capture": 96.0,
            "polish_efficiency": 88.0,
            "faradaic_eff": 92.0,
            "power_price": 35.0,
            "selling_price_ton": 13000.0,
        })
    elif mode_name == "Stressed Case":
        base.update({
            "li_capture": 90.0,
            "polish_efficiency": 73.0,
            "faradaic_eff": 84.0,
            "current_density": 520,
            "power_price": 85.0,
            "min_load_fraction": 0.30,
        })

    return base


# -----------------------------
# SESSION STATE / DEMO PRESETS
# -----------------------------
WIDGET_DEFAULTS_INITIALIZED = "widget_defaults_initialized"

def build_demo_values(feedstock_name, mode_name):
    preset = FEEDSTOCK_PRESETS[feedstock_name]
    mode_defaults = make_mode_preset(mode_name, preset)

    reference_capacity_tpy = 2000
    capacity_scale_factor = mode_defaults["target_capacity_tpy"] / reference_capacity_tpy
    scaled_flow_default = max(1.0, float(preset["flow_m3h"]) * capacity_scale_factor)
    scaled_stack_default = max(
        1,
        int(round(mode_defaults["stack_count"] * capacity_scale_factor / max(mode_defaults["target_capacity_tpy"], 1) * 2000))
    )
    scaled_stack_default = min(scaled_stack_default, 500)
    scaled_capex_default = scale_capex(24.0, capacity_scale_factor, mode_defaults["capex_scaling_exponent"])

    mg_default = float(preset["mg_gl"])
    ca_default = float(preset["ca_gl"])
    so4_default = float(preset["so4_gl"])
    b_default = float(preset["b_gl"])

    if mode_name == "Dirty Brine":
        mg_default = min(5.0, mg_default * 1.8 + 0.4)
        ca_default = min(5.0, ca_default * 1.6 + 0.2)
        so4_default = min(10.0, so4_default * 1.7 + 0.6)
        b_default = min(3.0, b_default * 1.4 + 0.1)

    return {
        "feed_mode": mode_defaults["feed_mode"],
        "target_capacity_tpy": int(mode_defaults["target_capacity_tpy"]),
        "reference_capacity_tpy": reference_capacity_tpy,
        "capex_scaling_exponent": float(mode_defaults["capex_scaling_exponent"]),
        "flow_m3h": min(scaled_flow_default, 1500.0),
        "li_conc": float(preset["li_conc"]),
        "uptime": float(mode_defaults["uptime"]),
        "mg_gl": mg_default,
        "ca_gl": ca_default,
        "na_gl": float(preset["na_gl"]),
        "k_gl": float(preset["k_gl"]),
        "so4_gl": so4_default,
        "b_gl": b_default,
        "li_capture": float(mode_defaults["li_capture"]),
        "wash_recovery": float(mode_defaults["wash_recovery"]),
        "polish_efficiency": float(mode_defaults["polish_efficiency"]),
        "faradaic_eff": float(mode_defaults["faradaic_eff"]),
        "current_density": int(mode_defaults["current_density"]),
        "cell_voltage": float(mode_defaults["cell_voltage"]),
        "current_per_stack": int(mode_defaults["current_per_stack"]),
        "active_area_per_stack": float(mode_defaults["active_area_per_stack"]),
        "stack_count": int(min(max(1, scaled_stack_default), 500)),
        "conversion_per_pass": float(mode_defaults["conversion_per_pass"]),
        "recycle_ratio": float(mode_defaults["recycle_ratio"]),
        "crystallizer_yield": float(mode_defaults["crystallizer_yield"]),
        "mother_liquor_recovery": float(mode_defaults["mother_liquor_recovery"]),
        "target_purity": float(mode_defaults["target_purity"]),
        "power_price": float(mode_defaults["power_price"]),
        "reagent_cost_ton": float(mode_defaults["reagent_cost_ton"]),
        "labor_maint_ton": float(mode_defaults["labor_maint_ton"]),
        "capex_m": min(scaled_capex_default, 500.0),
        "project_years": 15,
        "selling_price_ton": float(mode_defaults["selling_price_ton"]),
        "corporate_overhead_m": float(mode_defaults["corporate_overhead_m"]),
        "sustaining_capex_pct": 2.0,
        "flexibility_mode": bool(mode_defaults["flexibility_mode"]),
        "min_load_fraction": float(mode_defaults["min_load_fraction"]),
    }


def apply_demo_values(feedstock_name, mode_name):
    values = build_demo_values(feedstock_name, mode_name)
    for key, value in values.items():
        st.session_state[key] = value


if WIDGET_DEFAULTS_INITIALIZED not in st.session_state:
    st.session_state[WIDGET_DEFAULTS_INITIALIZED] = True
    st.session_state["selected_feedstock"] = list(FEEDSTOCK_PRESETS.keys())[0]
    st.session_state["selected_demo_preset"] = "Investor Case"
    apply_demo_values(st.session_state["selected_feedstock"], st.session_state["selected_demo_preset"])


# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="control-room-title">MONOLiTH Control Room</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="control-room-subtitle">Interactive pilot-plant digital twin for electrochemical LiOH·H₂O refining.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="control-room-caption">Use the demo presets to quickly show healthy operation, dirty-brine stress, low-cost power dispatch, or a higher-throughput scaling case.</div>',
    unsafe_allow_html=True,
)

with st.expander("How to use this digital twin"):
    st.markdown(
        """
        **Suggested demo flow**

        1. Choose a **Feedstock Source**
        2. Choose a **Demo Preset**
        3. Click **Load Demo Preset**
        4. Review the **Plant Overview Ribbon**
        5. Walk through the **Process Digital Twin**
        6. Use **Operator Alerts**, **Target Bands**, **Guardrail Checks**, and **Quick Plant Metrics**
        7. Finish with the **Economics + Power Flexibility Strip**

        This version lands in **Investor Case** by default so the first screen is polished for sharing.
        """
    )


# -----------------------------
# DEMO CONTROLS
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Demo Controls</div>', unsafe_allow_html=True)

d1, d2, d3 = st.columns([1.2, 1.4, 1.4])

with d1:
    selected_feedstock = st.selectbox(
        "Feedstock Source",
        list(FEEDSTOCK_PRESETS.keys()),
        key="selected_feedstock",
    )

with d2:
    selected_demo_preset = st.radio(
        "Demo Preset",
        ["Investor Case", "Base Case", "Low Cost Power", "Dirty Brine", "High Throughput", "Stressed Case"],
        horizontal=True,
        key="selected_demo_preset",
    )

with d3:
    st.write("")
    st.write("")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Load Demo Preset", use_container_width=True):
            apply_demo_values(st.session_state["selected_feedstock"], st.session_state["selected_demo_preset"])
            st.rerun()
    with b2:
        if st.button("Reset to Investor Case", use_container_width=True):
            st.session_state["selected_demo_preset"] = "Investor Case"
            apply_demo_values(st.session_state["selected_feedstock"], "Investor Case")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

preset_name = st.session_state["selected_feedstock"]
mode_name = st.session_state["selected_demo_preset"]
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
        key="target_capacity_tpy",
        step=250,
    )

with col2:
    reference_capacity_tpy = st.number_input(
        "Reference plant size for scaling (t/y)",
        min_value=100,
        max_value=50000,
        key="reference_capacity_tpy",
        step=100,
    )

with col3:
    capex_scaling_exponent = st.slider(
        "CAPEX scaling exponent",
        0.50,
        0.90,
        key="capex_scaling_exponent",
        step=0.01,
    )

capacity_scale_factor = safe_div(target_capacity_tpy, reference_capacity_tpy, default=1.0)
st.caption(
    f"Capacity scaling factor = {capacity_scale_factor:.2f}× relative to {reference_capacity_tpy:,} t/y reference."
)


# -----------------------------
# PROCESS ROUTE
# -----------------------------
st.header("Process Route")

feed_mode = st.selectbox(
    "Feed chemistry",
    ["LiCl", "Li2SO4"],
    key="feed_mode",
)


# -----------------------------
# FEED CONDITIONS
# -----------------------------
st.header("Feed Conditions")

col1, col2, col3 = st.columns(3)

with col1:
    flow_m3h = st.slider("Feed flow rate (m³/h)", 1.0, 1500.0, key="flow_m3h", step=1.0)
    li_conc = st.slider("Lithium concentration (g/L)", 0.1, 6.0, key="li_conc", step=0.1)
    uptime = st.slider("Plant uptime (%)", 60.0, 100.0, key="uptime", step=1.0)

with col2:
    mg_gl = st.slider("Mg concentration (g/L)", 0.0, 5.0, key="mg_gl", step=0.05)
    ca_gl = st.slider("Ca concentration (g/L)", 0.0, 5.0, key="ca_gl", step=0.05)
    na_gl = st.slider("Na concentration (g/L)", 0.0, 40.0, key="na_gl", step=0.5)

with col3:
    k_gl = st.slider("K concentration (g/L)", 0.0, 20.0, key="k_gl", step=0.2)
    so4_gl = st.slider("External sulfate concentration (g/L)", 0.0, 10.0, key="so4_gl", step=0.1)
    b_gl = st.slider("Boron concentration (g/L)", 0.0, 3.0, key="b_gl", step=0.05)


# -----------------------------
# CAPTURE + POLISHING
# -----------------------------
st.header("Capture + Polishing")

col1, col2, col3 = st.columns(3)
with col1:
    li_capture = st.slider("Lithium capture (%)", 70.0, 99.0, key="li_capture", step=0.5)
with col2:
    wash_recovery = st.slider("Wash recovery (%)", 85.0, 99.5, key="wash_recovery", step=0.5)
with col3:
    polish_efficiency = st.slider("Polishing efficiency (%)", 50.0, 99.0, key="polish_efficiency", step=1.0)


# -----------------------------
# ELECTROCHEMICAL STACK
# -----------------------------
st.header("Electrochemical Stack")

col1, col2, col3 = st.columns(3)
with col1:
    faradaic_eff = st.slider("Faradaic efficiency (%)", 60.0, 99.0, key="faradaic_eff", step=0.5)
    current_density = st.slider("Current density (A/m²)", 50, 800, key="current_density", step=10)

with col2:
    cell_voltage = st.slider("Cell voltage (V)", 2.5, 6.5, key="cell_voltage", step=0.1)
    current_per_stack = st.slider("Current per stack (A)", 100, 5000, key="current_per_stack", step=50)

with col3:
    active_area_per_stack = st.slider("Active area per stack (m²)", 0.5, 25.0, key="active_area_per_stack", step=0.5)
    stack_count = st.slider("Number of stacks", 1, 500, key="stack_count", step=1)

conversion_per_pass = st.slider("Conversion per pass (%)", 40.0, 98.0, key="conversion_per_pass", step=1.0)
recycle_ratio = st.slider("Recycle ratio (x)", 0.0, 8.0, key="recycle_ratio", step=0.1)


# -----------------------------
# CRYSTALLIZATION
# -----------------------------
st.header("Crystallization + Product")

col1, col2, col3 = st.columns(3)
with col1:
    crystallizer_yield = st.slider("Crystallizer yield (%)", 70.0, 99.0, key="crystallizer_yield", step=0.5)
with col2:
    mother_liquor_recovery = st.slider("Mother liquor recovery (%)", 0.0, 95.0, key="mother_liquor_recovery", step=1.0)
with col3:
    target_purity = st.slider("Target purity (wt%)", 98.0, 99.9, key="target_purity", step=0.1)


# -----------------------------
# ECONOMICS
# -----------------------------
st.header("Economics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    power_price = st.slider("Power price ($/MWh)", 10.0, 150.0, key="power_price", step=1.0)
    reagent_cost_ton = st.slider("Base reagent cost ($/t product)", 0.0, 2000.0, key="reagent_cost_ton", step=10.0)

with col2:
    labor_maint_ton = st.slider("Labor + maintenance ($/t product)", 100.0, 3000.0, key="labor_maint_ton", step=25.0)
    capex_m = st.slider("Installed CAPEX ($M)", 1.0, 500.0, key="capex_m", step=1.0)

with col3:
    project_years = st.slider("Project life (years)", 5, 25, key="project_years", step=1)
    selling_price_ton = st.slider("LiOH·H₂O selling price ($/t)", 4000.0, 30000.0, key="selling_price_ton", step=250.0)

with col4:
    corporate_overhead_m = st.slider("Corporate / SG&A ($M/y)", 0.0, 50.0, key="corporate_overhead_m", step=0.5)
    sustaining_capex_pct = st.slider("Sustaining CAPEX (% of installed CAPEX / y)", 0.0, 10.0, key="sustaining_capex_pct", step=0.5)


# -----------------------------
# POWER FLEXIBILITY SETTINGS
# -----------------------------
st.header("Power Flexibility Settings")

col1, col2 = st.columns(2)
with col1:
    flexibility_mode = st.toggle("Enable load-following power mode", key="flexibility_mode")
with col2:
    min_load_fraction = st.slider("Minimum turndown fraction", 0.10, 1.00, key="min_load_fraction", step=0.05)


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

raw_results = run_model(inputs)
results = sanitize_results(raw_results)

st.caption(
    f"Current basis: {results['route_name']} • Feedstock: {preset_name} • Demo preset: {mode_name} • Target capacity: {target_capacity_tpy:,} t/y"
)


# -----------------------------
# KPI CALCULATIONS
# -----------------------------
production_rate_tpy = max(0.0, results["lioh_tpy"])
production_rate_tpd = safe_div(results["lioh_tpy"], 365.0, default=0.0)
cost_per_ton = max(0.0, results["cash_cost_ton"])
energy_kwh_per_kg = max(0.0, results["specific_energy_kwh_kg"])
energy_kwh_per_ton = energy_kwh_per_kg * 1000.0
annual_energy_mwh = max(0.0, (results["power_kw"] * 24.0 * 365.0 * (uptime / 100.0)) / 1000.0)
gross_margin_ton = selling_price_ton - cost_per_ton
annual_revenue = max(0.0, production_rate_tpy * selling_price_ton)
annual_gross_profit = production_rate_tpy * gross_margin_ton
annual_sustaining_capex = max(0.0, capex_m * 1_000_000.0 * (sustaining_capex_pct / 100.0))
annual_ebitda_proxy = annual_gross_profit - (corporate_overhead_m * 1_000_000.0) - annual_sustaining_capex
ebitda_margin_pct = safe_div(annual_ebitda_proxy, annual_revenue, default=0.0) * 100.0 if annual_revenue > 0 else 0.0
capex_intensity = safe_div(capex_m * 1_000_000.0, max(target_capacity_tpy, 1.0), default=0.0)
simple_payback_years = safe_div(capex_m * 1_000_000.0, annual_ebitda_proxy, default=None) if annual_ebitda_proxy > 0 else None

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
health_text = health_label(health_score)

current_load_fraction = max(min_load_fraction, load_fraction_from_power_price(power_price)) if flexibility_mode else 1.0
current_load_fraction = clamp(current_load_fraction, 0.0, 1.0)

alerts = build_alerts(results, inputs, target_capacity_tpy, selling_price_ton, health_score, flexibility_mode)
guardrail_messages = build_guardrail_messages(results, inputs, target_capacity_tpy, selling_price_ton)


# -----------------------------
# TOP KPI RIBBON
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Plant Overview Ribbon</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    render_top_kpi("Production Rate", f"{production_rate_tpy:,.0f} t/y", f"{production_rate_tpd:,.2f} t/day")
with k2:
    render_top_kpi("Cash Cost", f"${cost_per_ton:,.0f}/t", f"Margin ${gross_margin_ton:,.0f}/t")
with k3:
    render_top_kpi("Energy Consumption", f"{energy_kwh_per_ton:,.0f} kWh/t", f"{energy_kwh_per_kg:,.2f} kWh/kg")
with k4:
    render_top_kpi("Product Purity", f"{results['purity_proxy']:.2f} wt%", f"Target {target_purity:.2f} wt%")
with k5:
    render_top_kpi("Stack Utilization", f"{results['utilization_pct']:.1f}%", f"{stack_count:,} installed stacks")
with k6:
    render_top_kpi("Plant Health", f"{health_score:.0f}/100", health_text)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# PROCESS DIGITAL TWIN
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Process Digital Twin</div>', unsafe_allow_html=True)
st.markdown(f'<div class="mode-pill">{mode_name}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="divider-note">Feed Tank → Capture Columns → Polishing → Electrochemical Stacks → Crystallizer → LiOH·H₂O Product</div>',
    unsafe_allow_html=True,
)

feed_status = [build_status_item("mg_gl", mg_gl), build_status_item("so4_gl", so4_gl)]
capture_status = [build_status_item("li_capture", li_capture)]
polishing_status = [build_status_item("polish_efficiency", polish_efficiency)]
stack_status = [
    build_status_item("current_density", current_density),
    build_status_item("faradaic_eff", faradaic_eff),
    build_status_item("specific_energy_kwh_kg", results["specific_energy_kwh_kg"]),
]
crystallizer_status = [build_status_item("cash_cost_ton", results["cash_cost_ton"])]
product_status = [build_status_item("cash_cost_ton", results["cash_cost_ton"])]

feed_level = unit_level_from_status_items(feed_status)
capture_level = unit_level_from_status_items(capture_status)
polishing_level = unit_level_from_status_items(polishing_status)
stack_level = unit_level_from_status_items(stack_status)
crystallizer_level = unit_level_from_status_items(crystallizer_status)
product_level = unit_level_from_status_items(product_status)

limiting_unit = bottleneck_unit_map(results["bottleneck"])

cols = st.columns([1.35, 0.28, 1.35, 0.28, 1.50, 0.28, 1.70, 0.28, 1.40, 0.28, 1.65])

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
        "Electrochemical Stacks",
        [
            f"{results['li_converted_kg_h']:.2f} kg Li/h converted",
            f"{results['power_kw']:,.0f} kW",
            f"{current_density} A/m²",
        ],
        stack_level,
        is_bottleneck=(limiting_unit == "Electrochemical Stacks"),
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

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# CONTROL ROOM SUPPORT PANELS
# -----------------------------
panel1, panel2, panel3, panel4 = st.columns([1, 1, 1, 1])

with panel1:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Operator Alerts</div>', unsafe_allow_html=True)
    for level, title, body in alerts:
        render_alert(level, title, body)
    st.markdown('</div>', unsafe_allow_html=True)

with panel2:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Target Bands</div>', unsafe_allow_html=True)

    st.write("**Cost position vs sell price**")
    render_cost_gauge(cost_per_ton, selling_price_ton)

    st.write("**Purity vs target**")
    purity_ratio = clamp(safe_div(results["purity_proxy"], max(target_purity, 1e-9), default=0.0), 0.0, 1.0)
    st.progress(purity_ratio)
    st.caption(f"{results['purity_proxy']:.2f} wt% actual vs {target_purity:.2f} wt% target")

    st.write("**Output vs target annual capacity**")
    output_ratio = clamp(safe_div(results["lioh_tpy"], max(target_capacity_tpy, 1e-9), default=0.0), 0.0, 1.0)
    st.progress(output_ratio)
    st.caption(f"{results['lioh_tpy']:,.0f} t/y actual vs {target_capacity_tpy:,.0f} t/y target")

    st.write("**Energy intensity band**")
    energy_ratio = clamp(safe_div(energy_kwh_per_kg, 20.0, default=0.0), 0.0, 1.0)
    st.progress(energy_ratio)
    st.caption(f"{energy_kwh_per_kg:.2f} kWh/kg current specific energy")

    st.markdown('</div>', unsafe_allow_html=True)

with panel3:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Quick Plant Metrics</div>', unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    with q1:
        st.metric("Li Feed", f"{results['li_feed_kg_h']:.2f} kg/h")
        st.metric("Capture Recovery", f"{results['capture_recovery_pct']:.1f}%")
        st.metric("Power Draw", f"{results['power_kw']:,.0f} kW")
    with q2:
        st.metric("Li Captured", f"{results['li_captured_kg_h']:.2f} kg/h")
        st.metric("Utilization", f"{results['utilization_pct']:.1f}%")
        st.metric("Annual Energy", f"{annual_energy_mwh:,.0f} MWh/y")

    st.markdown('</div>', unsafe_allow_html=True)

with panel4:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Guardrail Checks</div>', unsafe_allow_html=True)
    for level, title, body in guardrail_messages:
        render_guardrail_box(level, title, body)
    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# STACK FARM VISUALIZATION
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Stack Farm Visualization</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="divider-note">Blue stacks are currently online. Dim stacks are installed but idle under the current load-following condition. Orange stacks indicate stressed electrochemical operation. Large installations are shown as a representative operator sample view.</div>',
    unsafe_allow_html=True,
)

actual_active_count, display_count, displayed_active_count = infer_stack_cells(
    stack_count,
    current_load_fraction,
    max_display=48,
)

sf1, sf2, sf3, sf4 = st.columns(4)
with sf1:
    render_small_kpi("Installed Stacks", f"{stack_count:,}", "Total electrochemical modules installed")
with sf2:
    render_small_kpi("Stacks Online Now", f"{actual_active_count:,}", f"{current_load_fraction*100:.0f}% current operating load")
with sf3:
    render_small_kpi("Displayed Sample View", f"{display_count}", "Representative stacks shown visually on screen")
with sf4:
    render_wrapped_value_card("Current Stack Constraint", results["bottleneck"], "Primary electrochemical limitation reported by model")

stressed_stack_mode = (
    results["bottleneck"] in ["Installed stack current", "Membrane area / stack geometry"]
    or current_density >= 500
)

render_stack_farm(
    stack_count=stack_count,
    load_fraction=current_load_fraction,
    stressed=stressed_stack_mode,
    max_display=48,
    cols_per_row=8,
)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# ECONOMICS + POWER STRIP
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Economics + Power Flexibility Strip</div>', unsafe_allow_html=True)

econ1, econ2, econ3, econ4, econ5, econ6 = st.columns(6)
with econ1:
    render_small_kpi("Revenue Proxy", f"${annual_revenue/1_000_000:,.1f}M/y", "LiOH·H₂O selling price basis")
with econ2:
    render_small_kpi("EBITDA Proxy", f"${annual_ebitda_proxy/1_000_000:,.1f}M/y", f"{ebitda_margin_pct:,.1f}% EBITDA margin")
with econ3:
    render_small_kpi("CAPEX Intensity", f"${capex_intensity:,.0f}/t", "Installed capital / t capacity")
with econ4:
    render_small_kpi("Gross Margin / t", f"${gross_margin_ton:,.0f}/t", f"Sell ${selling_price_ton:,.0f}/t")
with econ5:
    render_small_kpi("Simple Payback", "N/A" if simple_payback_years is None else f"{simple_payback_years:,.1f} y", "Proxy only")
with econ6:
    render_small_kpi("Corporate / Sustain", f"${corporate_overhead_m:,.1f}M + ${annual_sustaining_capex/1_000_000:,.1f}M", "Overhead + sustaining CAPEX")

power_flex_rows = []
for price in [20.0, 40.0, 60.0, 80.0, 100.0]:
    base_load = load_fraction_from_power_price(price)
    load_fraction = max(min_load_fraction, base_load) if flexibility_mode else 1.0
    load_fraction = clamp(load_fraction, 0.0, 1.0)

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
            "LiOH_tpy": max(0.0, flex_lioh),
            "Power_kW": max(0.0, flex_power),
            "Revenue_$per_y": flex_revenue,
            "EBITDA_$per_y": flex_ebitda,
        }
    )

power_flex_df = pd.DataFrame(power_flex_rows)

c1, c2, c3 = st.columns([1.1, 1.1, 0.9])

with c1:
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

with c2:
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

with c3:
    st.dataframe(power_flex_df, use_container_width=True, height=300)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# HEALTH + OPERATING WINDOW
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Plant Health + Operating Window</div>', unsafe_allow_html=True)

h1, h2 = st.columns([1, 2])
with h1:
    st.metric("Plant Health Score", f"{health_score:.0f}/100")
    if health_score >= 85:
        st.success(health_text)
    elif health_score >= 60:
        st.warning(health_text)
    else:
        st.error(health_text)

with h2:
    red = sum(item["Level"] == "Red" for item in status_items)
    yellow = sum(item["Level"] == "Yellow" for item in status_items)
    green = sum(item["Level"] == "Green" for item in status_items)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Green", green)
    r2.metric("Yellow", yellow)
    r3.metric("Red", red)
    r4.markdown(
        f"""
        <div class="small-kpi">
            <div class="small-kpi-label">Bottleneck</div>
            <div style="color:#f8fafc; font-size:1.0rem; font-weight:800; line-height:1.25; white-space:normal; word-break:break-word;">
                {results["bottleneck"]}
            </div>
            <div class="small-kpi-sub">Current limiting factor</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

ow1, ow2 = st.columns(2)
with ow1:
    for item in status_items[:5]:
        render_status_box(item)
with ow2:
    for item in status_items[5:]:
        render_status_box(item)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# CAPACITY SCALING SUMMARY
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Capacity Scaling Summary</div>', unsafe_allow_html=True)

cs1, cs2, cs3, cs4 = st.columns(4)
cs1.metric("Target Capacity", f"{target_capacity_tpy:,} t/y")
cs2.metric("Flow Scale Factor", f"{capacity_scale_factor:.2f}×")
cs3.metric("Suggested Stack Count", f"{stack_count:,}")
cs4.metric("Installed CAPEX Basis", f"${capex_m:,.1f}M")

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# SCENARIO COMPARISON
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Scenario Comparison</div>', unsafe_allow_html=True)

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

res_a = sanitize_results(run_model(scenario_a))
res_b = sanitize_results(run_model(scenario_b))

comparison_df = pd.DataFrame(
    [
        {
            "Scenario": label_a,
            "Route": res_a["route_name"],
            "LiOH_tpy": max(0.0, res_a["lioh_tpy"]),
            "CashCost_$per_t": max(0.0, res_a["cash_cost_ton"]),
            "SpecificEnergy_kWh_per_kg": max(0.0, res_a["specific_energy_kwh_kg"]),
            "Purity_wt_pct": clamp(res_a["purity_proxy"], 0.0, 100.0),
            "Power_kW": max(0.0, res_a["power_kw"]),
            "CaptureRecovery_pct": clamp(res_a["capture_recovery_pct"], 0.0, 100.0),
            "ImpuritySeverity": max(0.0, res_a["impurity_severity"]),
            "Utilization_pct": clamp(res_a["utilization_pct"], 0.0, 100.0),
            "Bottleneck": res_a["bottleneck"],
        },
        {
            "Scenario": label_b,
            "Route": res_b["route_name"],
            "LiOH_tpy": max(0.0, res_b["lioh_tpy"]),
            "CashCost_$per_t": max(0.0, res_b["cash_cost_ton"]),
            "SpecificEnergy_kWh_per_kg": max(0.0, res_b["specific_energy_kwh_kg"]),
            "Purity_wt_pct": clamp(res_b["purity_proxy"], 0.0, 100.0),
            "Power_kW": max(0.0, res_b["power_kw"]),
            "CaptureRecovery_pct": clamp(res_b["capture_recovery_pct"], 0.0, 100.0),
            "ImpuritySeverity": max(0.0, res_b["impurity_severity"]),
            "Utilization_pct": clamp(res_b["utilization_pct"], 0.0, 100.0),
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

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# QUICK SENSITIVITY + CHARTS
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Sensitivity + Charts</div>', unsafe_allow_html=True)

sensitivity_metric = st.selectbox(
    "Sensitivity metric",
    ["LiOH_tpy", "CashCost_$per_t", "SpecificEnergy_kWh_per_kg"],
)

power_range = [20.0, 40.0, 60.0, 80.0, 100.0]
sens_rows = []
for price in power_range:
    sens_inputs = base_inputs.copy()
    sens_inputs["power_price"] = price
    sens_results = sanitize_results(run_model(sens_inputs))
    sens_rows.append(
        {
            "PowerPrice_$per_MWh": price,
            "LiOH_tpy": max(0.0, sens_results["lioh_tpy"]),
            "CashCost_$per_t": max(0.0, sens_results["cash_cost_ton"]),
            "SpecificEnergy_kWh_per_kg": max(0.0, sens_results["specific_energy_kwh_kg"]),
        }
    )

sensitivity_df = pd.DataFrame(sens_rows)

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

ch1, ch2 = st.columns(2)

with ch1:
    scenario_chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("Scenario:N", title="Scenario"),
            y=alt.Y(f"{metric_col}:Q", title=selected_metric),
            tooltip=["Scenario", "Route", metric_col],
        )
        .properties(title="Scenario Comparison", height=320)
    )
    st.altair_chart(scenario_chart, use_container_width=True)

with ch2:
    sensitivity_chart = (
        alt.Chart(sensitivity_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("PowerPrice_$per_MWh:Q", title="Power price ($/MWh)"),
            y=alt.Y(f"{sensitivity_metric}:Q", title=sensitivity_metric),
            tooltip=["PowerPrice_$per_MWh", sensitivity_metric],
        )
        .properties(title="Power Sensitivity", height=320)
    )
    st.altair_chart(sensitivity_chart, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# RAW OUTPUT + EXPORTS
# -----------------------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Model Output + Export</div>', unsafe_allow_html=True)

export_df = pd.DataFrame(
    [
        {
            "Feedstock": preset_name,
            "DemoPreset": mode_name,
            "Route": results["route_name"],
            "TargetCapacity_tpy": target_capacity_tpy,
            "LiOH_H2O_tpy": production_rate_tpy,
            "LiOH_H2O_tpd": production_rate_tpd,
            "CashCost_$per_t": cost_per_ton,
            "SellingPrice_$per_t": selling_price_ton,
            "SpecificEnergy_kWh_per_kg": energy_kwh_per_kg,
            "SpecificEnergy_kWh_per_t": energy_kwh_per_ton,
            "AnnualEnergy_MWh": annual_energy_mwh,
            "EBITDAProxy_$per_y": annual_ebitda_proxy,
            "HealthScore": health_score,
            "Bottleneck": results["bottleneck"],
        }
    ]
)

e1, e2 = st.columns([1, 2])
with e1:
    csv_out = io.StringIO()
    export_df.to_csv(csv_out, index=False)
    st.download_button(
        label="Download KPI summary CSV",
        data=csv_out.getvalue(),
        file_name="monolith_control_room_kpis.csv",
        mime="text/csv",
    )
with e2:
    with st.expander("Technical details"):
        st.json(results)

st.markdown('</div>', unsafe_allow_html=True)
