OPERATING_WINDOWS = {

    "current_density": {
        "label": "Current density",
        "units": "A/m²",
        "green_min": 250,
        "green_max": 450,
        "yellow_min": 150,
        "yellow_max": 550,
        "green_msg": "Operating in the preferred electrochemical window.",
        "yellow_msg": "Approaching reduced efficiency or higher stack stress.",
        "red_msg": "Outside preferred operating window; elevated degradation or weak economics may occur.",
    },

    "faradaic_eff": {
        "label": "Faradaic efficiency",
        "units": "%",
        "green_min": 88,
        "green_max": 99,
        "yellow_min": 80,
        "yellow_max": 88,
        "green_msg": "Strong electrochemical conversion efficiency.",
        "yellow_msg": "Conversion losses may begin to hurt economics.",
        "red_msg": "Poor conversion efficiency; cost and performance degraded.",
    },

    "mg_gl": {
        "label": "Mg concentration",
        "units": "g/L",
        "green_min": 0.0,
        "green_max": 0.20,
        "yellow_min": 0.20,
        "yellow_max": 0.50,
        "green_msg": "Impurity burden is comfortably manageable.",
        "yellow_msg": "Polishing load increasing.",
        "red_msg": "High divalent impurity burden; polishing stress likely.",
    },

    "so4_gl": {
        "label": "External sulfate",
        "units": "g/L",
        "green_min": 0.0,
        "green_max": 1.5,
        "yellow_min": 1.5,
        "yellow_max": 3.0,
        "green_msg": "Sulfate burden is favorable.",
        "yellow_msg": "Sulfate beginning to impact polishing.",
        "red_msg": "High sulfate burden; cost penalties likely.",
    },

    "power_price": {
        "label": "Power price",
        "units": "$/MWh",
        "green_min": 10,
        "green_max": 50,
        "yellow_min": 50,
        "yellow_max": 80,
        "green_msg": "Electricity price supports strong economics.",
        "yellow_msg": "Electricity becoming a cost pressure.",
        "red_msg": "Electricity price too high for competitive operation.",
    },

    "polish_efficiency": {
        "label": "Polishing efficiency",
        "units": "%",
        "green_min": 85,
        "green_max": 99,
        "yellow_min": 75,
        "yellow_max": 85,
        "green_msg": "Purification performance is strong.",
        "yellow_msg": "Purification acceptable but losing margin.",
        "red_msg": "Polishing insufficient for stable operation.",
    },

    "li_capture": {
        "label": "Lithium capture",
        "units": "%",
        "green_min": 92,
        "green_max": 99,
        "yellow_min": 85,
        "yellow_max": 92,
        "green_msg": "Capture efficiency is strong.",
        "yellow_msg": "Capture leaving some lithium unrecovered.",
        "red_msg": "Capture efficiency too low for economic viability.",
    },

    "specific_energy_kwh_kg": {
        "label": "Specific energy",
        "units": "kWh/kg",
        "green_min": 0.0,
        "green_max": 10.0,
        "yellow_min": 10.0,
        "yellow_max": 15.0,
        "green_msg": "Energy intensity is favorable.",
        "yellow_msg": "Energy intensity acceptable but should improve.",
        "red_msg": "Energy demand too high for commercial operation.",
    },

    "cash_cost_ton": {
        "label": "Cash cost",
        "units": "$/t",
        "green_min": 0.0,
        "green_max": 5000.0,
        "yellow_min": 5000.0,
        "yellow_max": 8000.0,
        "green_msg": "Cost profile commercially attractive.",
        "yellow_msg": "Cost elevated; optimization needed.",
        "red_msg": "Cost outside viable commercial range.",
    },

}


FEEDSTOCK_PRESETS = {
    "Synthetic benchmark": {
        "feed_mode": "LiCl",
        "flow_m3h": 35.0,
        "li_conc": 2.4,
        "mg_gl": 0.15,
        "ca_gl": 0.10,
        "na_gl": 10.0,
        "k_gl": 2.0,
        "so4_gl": 1.2,
        "b_gl": 0.20,
    },

    "Smackover-like brine": {
        "feed_mode": "LiCl",
        "flow_m3h": 40.0,
        "li_conc": 1.6,
        "mg_gl": 0.08,
        "ca_gl": 0.05,
        "na_gl": 18.0,
        "k_gl": 3.5,
        "so4_gl": 0.4,
        "b_gl": 0.10,
    },

    "Geothermal brine": {
        "feed_mode": "LiCl",
        "flow_m3h": 32.0,
        "li_conc": 1.1,
        "mg_gl": 0.35,
        "ca_gl": 0.20,
        "na_gl": 14.0,
        "k_gl": 4.0,
        "so4_gl": 2.2,
        "b_gl": 0.35,
    },

    "Dirty Li2SO4 case": {
        "feed_mode": "Li2SO4",
        "flow_m3h": 28.0,
        "li_conc": 2.0,
        "mg_gl": 0.55,
        "ca_gl": 0.30,
        "na_gl": 8.0,
        "k_gl": 1.5,
        "so4_gl": 3.5,
        "b_gl": 0.40,
    },

    "Clean Li2SO4 eluate": {
        "feed_mode": "Li2SO4",
        "flow_m3h": 30.0,
        "li_conc": 2.8,
        "mg_gl": 0.05,
        "ca_gl": 0.03,
        "na_gl": 5.0,
        "k_gl": 0.8,
        "so4_gl": 0.8,
        "b_gl": 0.05,
    },
}
