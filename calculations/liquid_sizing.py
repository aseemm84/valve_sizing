import numpy as np
from utils.unit_converters import convert_pressure, convert_flow_liquid, convert_density

def calculate_liquid_cv(data):
    """
    Calculates the required flow coefficient (Cv) for liquid service.
    Follows the ISA S75.01 / IEC 60534-2-1 standards.
    """
    # Convert units to a consistent base (Imperial for Cv calculation)
    p1 = convert_pressure(data['p1'], data['unit_system'], 'psi')
    p2 = convert_pressure(data['p2'], data['unit_system'], 'psi')
    pv = convert_pressure(data['pv'], data['unit_system'], 'psi')
    pc = convert_pressure(data['pc'], data['unit_system'], 'psi')
    flow_rate = convert_flow_liquid(data['flow_rate'], data['unit_system'], 'gpm')
    
    # Specific Gravity (Gf)
    if data['unit_system'] == 'Metric':
        # rho is in kg/m3, convert to specific gravity
        Gf = data['rho'] / 1000.0
    else:
        # rho is already specific gravity in Imperial
        Gf = data['rho']

    fl = data.get('fl', 0.9)
    kc = data.get('kc', 0.7)

    # Differential pressure
    dp = p1 - p2

    # Choked flow calculation (delta P allowable)
    ff = 0.96 - 0.28 * (pv / pc) ** 0.5
    dp_allowable = (fl ** 2) * (p1 - ff * pv)

    # Use the smaller of actual or allowable delta P
    dp_sizing = min(dp, dp_allowable)

    if dp_sizing <= 0:
        raise ValueError("Sizing pressure drop (dP) must be positive. Check inlet/outlet pressures.")

    # Calculate Cv
    cv = flow_rate * (Gf / dp_sizing) ** 0.5

    # Flashing and Cavitation Analysis
    is_flashing = p2 < pv
    sigma = (p1 - pv) / (p1 - p2)
    cavitation_index = sigma

    if is_flashing:
        cavitation_status = "Flashing Occurs"
        trim_recommendation = "Flashing service requires hardened trim materials (e.g., Stellite) and potentially an expanded outlet."
    elif cavitation_index < (1 / kc):
        cavitation_status = "Cavitation Likely"
        trim_recommendation = "High cavitation risk. Recommend using anti-cavitation trim or a multi-stage valve design."
    else:
        cavitation_status = "No Significant Cavitation"
        trim_recommendation = "Standard trim is likely acceptable, but monitor for high pressure drop scenarios."

    return {
        "cv": cv,
        "is_flashing": is_flashing,
        "cavitation_index": cavitation_index,
        "cavitation_status": cavitation_status,
        "trim_recommendation": trim_recommendation,
        "dp_sizing": dp_sizing
    }

