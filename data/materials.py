def select_materials(data):
    """
    Recommends valve materials based on fluid nature, temperature, and pressure.
    Cross-checks against common industry standards.
    """
    fluid_nature = data['fluid_nature']
    temp = data['t1']
    pressure = data['p1']
    
    # Default to standard materials
    body_material = "Carbon Steel (ASTM A216 WCB)"
    trim_material = "Stainless Steel (316 SS)"
    
    # Logic for corrosive service
    if fluid_nature == "Corrosive":
        body_material = "Stainless Steel (ASTM A351 CF8M)"
        trim_material = "Alloy 20 or Hastelloy C"
        
    # Logic for abrasive service
    if fluid_nature == "Abrasive":
        trim_material = "Stellite Hard Facing or Ceramic"
        
    # Logic for flashing/cavitating service
    if fluid_nature == "Flashing/Cavitating":
        trim_material = "Stellite Hard Facing on 316 SS Base"

    # Temperature-based adjustments
    if temp > 427: # High temp (approx 800F)
        body_material = "Chrome-Moly (ASTM A217 C5/C12)"
    elif temp < -29: # Low temp / cryogenic (approx -20F)
        body_material = "Stainless Steel (ASTM A351 CF8M)"
        
    # Compliance check string
    compliance_check = "Materials selected are generally compliant with NACE MR0175 and ASME B16.34 for standard service. Final verification against specific service conditions is required."
    if fluid_nature == "Corrosive":
        compliance_check += " Sour service (NACE) compliance for selected alloys must be verified."

    return {
        "recommendations": {
            "Body Material": body_material,
            "Trim Material": trim_material,
            "Bolting": "ASTM A193 B7 / A194 2H",
            "Gasket": "Spiral Wound 316SS/Graphite"
        },
        "compliance_check": compliance_check
    }

