# Conversion constants
BAR_TO_PSI = 14.5038
M3HR_TO_GPM = 4.40287
NM3HR_TO_SCFH = 37.324 # Approximate, based on standard engineering practice

def convert_pressure(value, from_system, to_unit):
    """Converts pressure between Metric (bar) and Imperial (psi)."""
    if from_system == 'Metric' and to_unit == 'psi':
        return value * BAR_TO_PSI
    if from_system == 'Imperial' and to_unit == 'bar':
        return value / BAR_TO_PSI
    return value # No conversion needed

def convert_flow_liquid(value, from_system, to_unit):
    """Converts liquid flow rate between Metric (m³/hr) and Imperial (gpm)."""
    if from_system == 'Metric' and to_unit == 'gpm':
        return value * M3HR_TO_GPM
    if from_system == 'Imperial' and to_unit == 'm³/hr':
        return value / M3HR_TO_GPM
    return value

def convert_density(value, from_system, to_unit):
    """Converts liquid density between Metric (kg/m³) and Imperial (SG)."""
    if from_system == 'Metric' and to_unit == 'SG':
        return value / 1000.0
    if from_system == 'Imperial' and to_unit == 'kg/m³':
        return value * 1000.0
    return value
    
def convert_temperature(value, from_system, to_unit):
    """Converts temperature between Metric (°C) and Imperial (°F)."""
    if from_system == 'Metric' and to_unit == '°F':
        return (value * 9/5) + 32
    if from_system == 'Imperial' and to_unit == '°C':
        return (value - 32) * 5/9
    return value

def convert_flow_gas(value, from_system, to_unit):
    """Converts gas flow rate between Metric (Nm³/hr) and Imperial (scfh)."""
    if from_system == 'Metric' and to_unit == 'scfh':
        return value * NM3HR_TO_SCFH
    if from_system == 'Imperial' and to_unit == 'Nm³/hr':
        return value / NM3HR_TO_SCFH
    return value

