import numpy as np
from utils.unit_converters import convert_pressure, convert_flow_gas, convert_temperature
from data import valve_data

def calculate_gas_cv(data):
    """
    Calculates the required flow coefficient (Cv) for gas or vapor service.
    Follows the ISA S75.01 / IEC 60534-2-1 standards.
    """
    p1_abs = convert_pressure(data['p1'], data['unit_system'], 'psia')
    p2_abs = convert_pressure(data['p2'], data['unit_system'], 'psia')
    t1_abs = convert_temperature(data['t1'], data['unit_system'], 'R')
    flow_rate_scfh = convert_flow_gas(data['flow_rate'], data['unit_system'], 'scfh')
    
    mw = data['mw']
    k = data['k']
    z = data['z']
    
    # Get valve-specific Xt from data file
    valve_specifics = valve_data.get_valve_data(data['valve_type'], data['valve_style'])
    xt = valve_specifics.get('Xt', 0.75) # Use selected Xt, default to 0.75 if not found
    
    # Ratio of specific heats factor
    fk = k / 1.40
    
    # Pressure drop ratio
    x = (p1_abs - p2_abs) / p1_abs
    
    # Choked flow condition
    x_choked = xt * fk
    
    if x >= x_choked:
        # Flow is choked (critical)
        x_sizing = x_choked
        is_choked = True
    else:
        # Flow is sub-critical
        x_sizing = x
        is_choked = False
        
    # Expansion factor Y
    y = 1 - (x_sizing / (3 * fk * xt))
    
    # Calculate Cv
    # Formula for Imperial units: Cv = Q / (1360 * Y * P1 * sqrt(x / (MW * T1 * Z)))
    denominator = 1360 * y * p1_abs * np.sqrt(x_sizing / (mw * t1_abs * z))
    if denominator == 0:
        raise ValueError("Calculation error: denominator is zero. Check inputs.")
        
    cv = flow_rate_scfh / denominator

    return {
        "cv": cv,
        "is_choked": is_choked,
        "expansion_factor_y": y,
        "pressure_drop_ratio_x": x,
        "choked_pressure_drop_ratio": x_choked
    }

