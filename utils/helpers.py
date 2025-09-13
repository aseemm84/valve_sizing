import plotly.graph_objects as go
import numpy as np

UNITS = {
    'Metric': {
        'pressure': 'bar',
        'temperature': '°C',
        'flow_liquid': 'm³/hr',
        'flow_gas': 'Nm³/hr',
        'density': 'kg/m³',
        'viscosity': 'cP',
        'force': 'N',
        'torque': 'Nm'
    },
    'Imperial': {
        'pressure': 'psi',
        'temperature': '°F',
        'flow_liquid': 'gpm',
        'flow_gas': 'scfh',
        'density': 'SG',
        'viscosity': 'cP',
        'force': 'lbf',
        'torque': 'ft-lbf'
    }
}

def get_units(unit_system):
    return UNITS.get(unit_system, UNITS['Metric'])

def recommend_characteristic(data):
    """Recommends a valve characteristic based on process conditions."""
    p1 = data.get('p1', 1)
    dp = data.get('dp', 1)
    
    # If pressure drop is a large percentage of inlet pressure, system is more linear
    # and a more non-linear valve (Equal Percentage) is needed.
    if (dp / p1) > 0.35:
        return "Equal Percentage"
    else:
        return "Linear"

def plot_valve_characteristic(data, calculated_cv):
    """Plots the inherent vs installed valve characteristic curve."""
    valve_char = data.get('valve_char', 'Equal Percentage')
    rated_cv = data.get('rated_cv', calculated_cv * 2) # Estimate if not available
    
    travel = np.linspace(0, 100, 101) # Percent open
    
    # Inherent Characteristic (assumes constant pressure drop)
    if valve_char == 'Linear':
        inherent_cv = (travel / 100) * rated_cv
    elif valve_char == 'Quick Opening':
        # Approximate quick opening curve
        inherent_cv = np.sqrt(travel / 100) * rated_cv
    else: # Equal Percentage
        R = data.get('inherent_rangeability', 50) # Use actual rangeability
        inherent_cv = rated_cv * (R ** ((travel / 100) - 1))

    inherent_cv = np.clip(inherent_cv, 0, rated_cv)

    # Installed Characteristic (simplified model)
    # This is a placeholder for a more complex calculation involving system pressure drop
    installed_cv = inherent_cv * 0.85 # Assume some pressure loss in the system

    # Create plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=travel, y=inherent_cv, mode='lines', name='Inherent Characteristic'))
    fig.add_trace(go.Scatter(x=travel, y=installed_cv, mode='lines', name='Estimated Installed', line=dict(dash='dash')))
    
    # Add operating point
    op_travel = (calculated_cv / rated_cv) * 100 if rated_cv > 0 else 0
    if 0 <= op_travel <= 100:
        fig.add_trace(go.Scatter(
            x=[op_travel], y=[calculated_cv],
            mode='markers', name='Operating Point',
            marker=dict(color='red', size=12, symbol='x')
        ))

    fig.update_layout(
        title='Valve Dynamic Characteristic Curve',
        xaxis_title='Valve Travel (% Open)',
        yaxis_title='Flow Coefficient (Cv)',
        legend_title='Characteristic',
        template='plotly_dark'
    )
    return fig

