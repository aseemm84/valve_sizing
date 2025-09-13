"""
This file contains typical characteristic coefficients for various control valve types and styles.
In a real-world, highly accurate application, this data would come from extensive manufacturer catalogs.
The values here are representative for general engineering purposes.
"""

VALVE_COEFFICIENTS = {
    "Globe": {
        "Standard, Cage-Guided": {
            "FL": 0.90, "Kc": 0.70, "Xt": 0.75, "Rangeability": 50,
            "Style": "General purpose, excellent throttling, moderate capacity."
        },
        "Low-Noise, Multi-Path": {
            "FL": 0.95, "Kc": 0.80, "Xt": 0.80, "Rangeability": 40,
            "Style": "Designed to attenuate aerodynamic noise in gas service."
        },
        "Anti-Cavitation, Multi-Stage": {
            "FL": 0.98, "Kc": 0.85, "Xt": 0.85, "Rangeability": 30,
            "Style": "Reduces pressure in multiple steps to prevent cavitation damage."
        },
        "Port-Guided, Quick Opening": {
            "FL": 0.85, "Kc": 0.65, "Xt": 0.70, "Rangeability": 20,
            "Style": "Best for on/off service, poor throttling."
        }
    },
    "Ball (Segmented)": {
        "Standard V-Notch": {
            "FL": 0.80, "Kc": 0.60, "Xt": 0.40, "Rangeability": 100,
            "Style": "Good rangeability and throttling, suitable for slurries."
        },
        "High-Performance": {
            "FL": 0.75, "Kc": 0.55, "Xt": 0.35, "Rangeability": 80,
            "Style": "Higher capacity, but less pressure recovery."
        }
    },
    "Butterfly": {
        "Standard, Centric Disc": {
            "FL": 0.70, "Kc": 0.50, "Xt": 0.30, "Rangeability": 20,
            "Style": "Low cost, high capacity, limited throttling range (typically 60-degree opening)."
        },
        "High-Performance, Double Offset": {
            "FL": 0.85, "Kc": 0.65, "Xt": 0.55, "Rangeability": 50,
            "Style": "Better shutoff and control than standard butterfly valves."
        }
    }
}

VALVE_RATED_CVS = {
    # Size (inches): Typical Rated Cv for a high-capacity valve
    1: 12,
    2: 50,
    3: 110,
    4: 170,
    6: 400,
    8: 700,
    10: 1080,
    12: 1750,
    14: 2400,
    16: 3200,
    18: 4100,
    20: 5000,
    24: 7200,
    30: 11000,
    36: 16000,
    42: 22000,
    48: 28000,
    54: 36000,
    60: 45000,
    66: 54000,
    72: 65000,
}

def get_valve_data(valve_type, valve_style):
    """Retrieves the characteristic coefficients for a specific valve type and style."""
    try:
        return VALVE_COEFFICIENTS[valve_type][valve_style]
    except KeyError:
        return {"FL": 0.9, "Kc": 0.7, "Xt": 0.75, "Rangeability": 30, "Style": "Default general purpose values."}

def get_valve_styles(valve_type):
    """Returns a list of available styles for a given valve type."""
    try:
        return list(VALVE_COEFFICIENTS[valve_type].keys())
    except KeyError:
        return ["Default Style"]

def get_rated_cv(valve_size):
    """Retrieves the typical rated Cv for a given valve size."""
    return VALVE_RATED_CVS.get(valve_size, 50) # Default to 50 if size not found

