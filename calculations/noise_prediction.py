import numpy as np

def predict_noise(inputs, results):
    """
    Simplified noise prediction based on the IEC 60534-8-3 model.
    This is a representative model and not a substitute for vendor-specific software.
    """
    p1 = inputs['p1']
    p2 = inputs['p2']
    valve_type = inputs['valve_type']
    
    dp = p1 - p2
    cv = results['cv']

    # Simplified sound power level calculation
    # Base noise level (Lw) depends heavily on pressure drop and flow
    # This is a highly simplified empirical formula for demonstration
    if inputs['fluid_type'] == 'Liquid':
        # Liquid noise is primarily from cavitation/flashing
        if results.get('cavitation_status') == "Cavitation Likely":
            base_noise = 80 + 10 * np.log10(dp * cv)
        elif results.get('is_flashing'):
            base_noise = 85 + 10 * np.log10(dp * cv)
        else:
            base_noise = 60 + 10 * np.log10(dp * cv)
    else: # Gas
        # Gas noise is primarily aerodynamic
        mach_velocity_simplified = 0.1 + (dp/p1) * 0.8 # Simplified proxy for mach number
        base_noise = 70 + 20 * np.log10(mach_velocity_simplified * 1000) + 10 * np.log10(cv)

    # Adjustments for valve type (transmission loss)
    if valve_type == "Globe":
        transmission_loss = -5
    elif valve_type == "Ball (Segmented)":
        transmission_loss = -10
    elif valve_type == "Butterfly":
        transmission_loss = -15
    else:
        transmission_loss = 0
        
    # Pipe wall thickness correction (assuming standard schedule 40 pipe)
    pipe_correction = -5

    # Total predicted noise at 1m (dBA)
    total_noise_dba = base_noise + transmission_loss + pipe_correction
    total_noise_dba = max(50, min(120, total_noise_dba)) # Cap the values to a realistic range

    # Recommendation logic
    if total_noise_dba > 110:
        noise_recommendation = "Extreme noise level. A specialized low-noise, multi-stage valve and path treatment (insulation, heavy-wall pipe) are essential."
    elif total_noise_dba > 85:
        noise_recommendation = "High noise level. Consider a low-noise trim package. Source treatment (thicker pipe) or path treatment (acoustic insulation) may be required."
    else:
        noise_recommendation = "Standard trim is acceptable from a noise perspective."

    return {
        "total_noise_dba": total_noise_dba,
        "noise_recommendation": noise_recommendation
    }

