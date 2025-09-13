from utils.unit_converters import convert_pressure

def size_actuator(inputs, results):
    """
    Calculates the required actuator thrust or torque.
    This is a simplified calculation; vendor software is required for final selection.
    """
    valve_type = inputs['valve_type']
    valve_size = inputs['valve_size_nominal']
    p1 = convert_pressure(inputs['p1'], inputs['unit_system'], 'psi')
    dp = convert_pressure(inputs['dp'], inputs['unit_system'], 'psi')
    
    # Estimate valve seat area (pi * r^2)
    seat_area = 3.14159 * (valve_size / 2)**2

    required_force = 0
    required_torque = 0
    actuator_recommendation = ""
    
    if valve_type == 'Globe':
        # Thrust calculation: Force = Area * Pressure
        # Unbalanced force from process fluid is the primary factor
        unbalanced_force = seat_area * dp
        
        # Add safety factor (e.g., 1.3 to 1.5)
        required_force = unbalanced_force * 1.3
        
        # Convert to Newtons if Metric
        if inputs['unit_system'] == 'Metric':
            required_force *= 4.44822 # lbf to N
        
        actuator_recommendation = f"A pneumatic spring-diaphragm or piston actuator capable of providing at least {required_force:.2f} {inputs['units']['force']} of thrust is recommended."

    else: # Butterfly or Ball
        # Torque is more complex, involving hydrodynamic and bearing friction forces.
        # This is a simplified estimation using a "torque factor".
        # Torque Factor (TF) in ft-lb/psi of dP
        if valve_type == 'Butterfly':
            torque_factor = 0.5 * valve_size 
        else: # Ball
            torque_factor = 0.7 * valve_size
            
        seating_torque = torque_factor * dp
        
        # Add safety factor
        required_torque = seating_torque * 1.5
        
        # Convert to Nm if Metric
        if inputs['unit_system'] == 'Metric':
            required_torque *= 1.35582 # ft-lbf to Nm
            
        actuator_recommendation = f"A pneumatic or electric rotary actuator (e.g., rack-and-pinion) capable of providing at least {required_torque:.2f} {inputs['units']['torque']} of torque is recommended."

    return {
        "required_force": required_force,
        "required_torque": required_torque,
        "actuator_recommendation": actuator_recommendation
    }

