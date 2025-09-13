import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Import calculation modules from subdirectories
from calculations import liquid_sizing, gas_sizing, noise_prediction, actuator_sizing
from data import materials, valve_data
from reporting import pdf_generator
from utils import helpers

st.set_page_config(layout="wide", page_title="Control Valve Sizing & Selection")

# --- APP STATE INITIALIZATION ---
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.input_data = {}
    st.session_state.results = {}
    st.session_state.unit_system = 'Metric'

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://placehold.co/300x100/003366/FFFFFF?text=VALV-SIZ", use_column_width=True)
    st.title("Navigation")
    st.write("---")
    st.session_state.unit_system = st.radio("Select Unit System", ('Metric', 'Imperial'), horizontal=True, key='unit_system_radio')
    units = helpers.get_units(st.session_state.unit_system)
    st.info(f"**Current Step:** {st.session_state.step} of 6")
    st.progress(st.session_state.step / 6)
    st.write("---")
    st.write("**Standards Compliance:**")
    st.success("✅ ISA S75 / IEC 60534")
    st.success("✅ API 6D")
    st.success("✅ NACE MR0175")
    st.success("✅ ASME B16.34")
    st.write("---")
    st.write("App developed as an industry benchmark.")

# --- MAIN APPLICATION WIZARD ---
st.title("Control Valve Sizing and Selection Wizard")

# --- STEP 1: Process Conditions ---
if st.session_state.step == 1:
    st.header("Step 1: Process Conditions")
    if 'step1_data' not in st.session_state:
        st.session_state.step1_data = {
            "fluid_type": "Liquid", "fluid_name": "Water", "fluid_nature": "Clean",
            "p1": 10.0, "p2": 5.0, "t1": 25.0, "flow_rate": 100.0,
            "rho": 1000.0 if st.session_state.unit_system == 'Metric' else 1.0,
            "pv": 0.03, "pc": 221.0, "vc": 1.0, "mw": 28.97, "z": 1.0, "k": 1.4,
        }
    s1_data = st.session_state.step1_data
    st.subheader("Fluid Information")
    s1_data['fluid_type'] = st.selectbox("Fluid Type", ["Liquid", "Gas/Vapor"], index=["Liquid", "Gas/Vapor"].index(s1_data['fluid_type']), help="Select if the process medium is a liquid or a gas/vapor.")
    s1_data['fluid_name'] = st.text_input("Fluid Name", value=s1_data['fluid_name'], help="Enter the common name of the fluid.")
    s1_data['fluid_nature'] = st.selectbox("Fluid Nature", ["Clean", "Corrosive", "Abrasive", "Flashing/Cavitating"], index=["Clean", "Corrosive", "Abrasive", "Flashing/Cavitating"].index(s1_data['fluid_nature']), help="Characterize the fluid to aid material selection.")
    st.subheader("Operating Conditions")
    col1, col2, col3 = st.columns(3)
    with col1:
        s1_data['p1'] = st.number_input(f"Inlet Pressure (P1) [{units['pressure']}]", min_value=0.1, value=s1_data['p1'], step=0.1, help="Pressure at the valve inlet.")
        s1_data['t1'] = st.number_input(f"Inlet Temperature (T1) [{units['temperature']}]", value=s1_data['t1'], help="Temperature at the valve inlet.")
        s1_data['flow_rate'] = st.number_input(f"Flow Rate (Q) [{units['flow_liquid' if s1_data['fluid_type'] == 'Liquid' else 'flow_gas']}]", min_value=0.1, value=s1_data['flow_rate'], step=1.0, help="Required flow rate through the valve.")
    with col2:
        s1_data['p2'] = st.number_input(f"Outlet Pressure (P2) [{units['pressure']}]", min_value=0.1, value=s1_data['p2'], step=0.1, help="Pressure at the valve outlet.")
        if s1_data['fluid_type'] == "Liquid":
            s1_data['rho'] = st.number_input(f"Density / Specific Gravity [{units['density']}]", value=s1_data['rho'], min_value=0.1, help="For Metric, use Density in kg/m³. For Imperial, use Specific Gravity (Water=1).")
            s1_data['pv'] = st.number_input(f"Vapor Pressure (Pv) [{units['pressure']}]", value=s1_data['pv'], min_value=0.0, help="Absolute vapor pressure of the liquid at inlet temperature.")
        else:
            s1_data['mw'] = st.number_input("Molecular Weight (MW)", value=s1_data['mw'], min_value=1.0, help="Molecular weight of the gas (e.g., Air=28.97).")
            s1_data['z'] = st.number_input("Compressibility Factor (Z)", value=s1_data['z'], min_value=0.2, max_value=2.0, help="Compressibility factor at inlet conditions. Use 1.0 for ideal gases.")
    with col3:
        dp = s1_data['p1'] - s1_data['p2']
        st.metric(label=f"Differential Pressure (ΔP) [{units['pressure']}]", value=f"{dp:.2f}")
        if s1_data['fluid_type'] == "Liquid":
            s1_data['pc'] = st.number_input(f"Critical Pressure (Pc) [{units['pressure']}]", value=s1_data['pc'], min_value=0.1, help="Absolute critical pressure of the liquid.")
            s1_data['vc'] = st.number_input(f"Viscosity [{units['viscosity']}]", value=s1_data['vc'], min_value=0.1, help="Liquid viscosity at inlet temperature.")
        else:
            s1_data['k'] = st.number_input("Specific Heat Ratio (k = Cp/Cv)", value=s1_data['k'], min_value=1.0, max_value=2.0, help="Ratio of specific heats for the gas.")
    if st.button("Save and Go to Step 2 ➡️"):
        if s1_data['p1'] <= s1_data['p2']:
            st.error("Error: Inlet Pressure (P1) must be greater than Outlet Pressure (P2). Please correct the values.")
        else:
            st.session_state.input_data = s1_data.copy()
            st.session_state.input_data['dp'] = dp
            st.session_state.input_data['units'] = units
            st.session_state.input_data['unit_system'] = st.session_state.unit_system
            del st.session_state.step1_data
            next_step()
            st.rerun()

# --- STEP 2: Valve Type and Characteristics ---
elif st.session_state.step == 2:
    st.header("Step 2: Valve Type and Characteristics")
    if 'step2_data' not in st.session_state:
        initial_valve_type = "Globe"
        initial_valve_styles = valve_data.get_valve_styles(initial_valve_type)
        initial_valve_style = initial_valve_styles[0]
        initial_valve_data = valve_data.get_valve_data(initial_valve_type, initial_valve_style)
        st.session_state.step2_data = {'valve_type': initial_valve_type, 'valve_style': initial_valve_style, 'valve_char': "Equal Percentage", 'valve_size_nominal': 2, 'fl': initial_valve_data.get('FL', 0.9), 'kc': initial_valve_data.get('Kc', 0.7)}
    s2_data = st.session_state.step2_data
    col1, col2 = st.columns(2)
    with col1:
        valve_types = ["Globe", "Ball (Segmented)", "Butterfly"]
        new_valve_type = st.selectbox("Select Valve Type", valve_types, index=valve_types.index(s2_data['valve_type']), help="Select the mechanical type of the valve.")
        available_styles = valve_data.get_valve_styles(new_valve_type)
        if new_valve_type != s2_data['valve_type']:
            s2_data['valve_type'] = new_valve_type
            s2_data['valve_style'] = available_styles[0]
            st.rerun()
        new_valve_style = st.selectbox("Select Valve Style / Trim", available_styles, index=available_styles.index(s2_data['valve_style']), help="Select the internal trim design. This significantly impacts performance.")
        if new_valve_style != s2_data['valve_style']:
            s2_data['valve_style'] = new_valve_style
            valve_specific_data = valve_data.get_valve_data(s2_data['valve_type'], s2_data['valve_style'])
            s2_data['fl'] = valve_specific_data.get('FL', 0.9)
            s2_data['kc'] = valve_specific_data.get('Kc', 0.7)
            st.rerun()
        rec_char = helpers.recommend_characteristic(st.session_state.input_data)
        st.info(f"**Recommendation:** Based on your process, an **{rec_char}** characteristic is recommended for better control.")
        s2_data['valve_char'] = st.selectbox("Valve Characteristic", ["Equal Percentage", "Linear", "Quick Opening"], help="Select the relationship between valve travel and flow rate.")
    with col2:
        globe_sizes = [1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24]
        large_sizes = globe_sizes + [30, 36, 42, 48, 54, 60, 66, 72]
        if s2_data['valve_type'] == 'Globe':
            available_sizes = globe_sizes
        else:
            available_sizes = large_sizes
        if s2_data['valve_size_nominal'] not in available_sizes:
            s2_data['valve_size_nominal'] = available_sizes[0]
        current_size_index = available_sizes.index(s2_data['valve_size_nominal'])
        s2_data['valve_size_nominal'] = st.selectbox("Nominal Valve Size (inches)", available_sizes, index=current_size_index, help="Select the nominal pipe size for the valve. Available sizes depend on valve type.")
        valve_specific_data = valve_data.get_valve_data(s2_data['valve_type'], s2_data['valve_style'])
        st.write("**Typical Valve Coefficients:**")
        st.json(valve_specific_data)
        s2_data['fl'] = st.number_input("Liquid Pressure Recovery Factor (FL)", value=s2_data['fl'], step=0.01, help="Override if you have specific vendor data. Value is suggested by valve style.")
        s2_data['kc'] = st.number_input("Cavitation Index Factor (Kc)", value=s2_data['kc'], step=0.01, help="Override if you have specific vendor data. Value is suggested by valve style.")
    if st.button("Save and Go to Step 3 ➡️"):
        st.session_state.input_data.update(s2_data)
        del st.session_state.step2_data
        next_step()
        st.rerun()
    st.button("⬅️ Back to Step 1", on_click=prev_step)

# --- STEP 3: Sizing Calculations ---
elif st.session_state.step == 3:
    st.header("Step 3: Sizing Calculation Results")
    try:
        if st.session_state.input_data['fluid_type'] == 'Liquid':
            results = liquid_sizing.calculate_liquid_cv(st.session_state.input_data)
        else:
            results = gas_sizing.calculate_gas_cv(st.session_state.input_data)
        st.session_state.results.update(results)
        st.subheader("Required Flow Coefficient (Cv)")
        st.metric("Calculated Cv", f"{results['cv']:.2f}")
        st.info("This is the required Cv for the specified flow conditions. A valve with a rated Cv greater than this value should be selected.")
        if 'cavitation_index' in results:
            with st.expander("Flashing and Cavitation Analysis", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Cavitation Index (Sigma)", f"{results['cavitation_index']:.2f}")
                with col2: st.metric("Flashing Status", "Yes" if results['is_flashing'] else "No")
                with col3: st.metric("Cavitation Status", results['cavitation_status'])
                st.warning(f"**Recommendation:** {results['trim_recommendation']}")
        with st.expander("Rangeability Analysis", expanded=True):
            try:
                valve_size = st.session_state.input_data['valve_size_nominal']
                valve_type = st.session_state.input_data['valve_type']
                valve_style = st.session_state.input_data['valve_style']
                valve_specifics = valve_data.get_valve_data(valve_type, valve_style)
                inherent_rangeability = valve_specifics.get("Rangeability", 30)
                rated_cv = valve_data.get_rated_cv(valve_size)
                min_cv = rated_cv / inherent_rangeability
                st.session_state.results['inherent_rangeability'] = inherent_rangeability
                st.session_state.results['rated_cv'] = rated_cv
                st.session_state.results['min_controllable_cv'] = min_cv
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Inherent Rangeability", f"{inherent_rangeability}:1", help="The ratio of max to min controllable flow for the selected valve style.")
                with col2:
                    st.metric(f"Rated Cv for {valve_size}\" Valve", f"{rated_cv}", help="The typical maximum Cv for the selected valve size.")
                st.info(f"The minimum controllable Cv for this selection is approximately **{min_cv:.2f}**.")
                calculated_cv = st.session_state.results['cv']
                if calculated_cv < min_cv:
                    st.error(f"**Oversized Valve Warning:** The required Cv ({calculated_cv:.2f}) is below the minimum controllable Cv ({min_cv:.2f}). Control at this flow rate will be poor. Consider selecting a smaller valve size.")
                    st.session_state.results['rangeability_status'] = "Valve Oversized"
                elif calculated_cv > rated_cv:
                    st.error(f"**Undersized Valve Warning:** The required Cv ({calculated_cv:.2f}) exceeds the rated Cv of the selected valve ({rated_cv}). The valve cannot meet the required flow. Select a larger valve size.")
                    st.session_state.results['rangeability_status'] = "Valve Undersized"
                else:
                    opening_percent = (calculated_cv / rated_cv) * 100
                    st.success(f"**Acceptable Sizing:** The required Cv ({calculated_cv:.2f}) is within the controllable range of the selected valve. The valve will be approximately **{opening_percent:.1f}% open** at this operating point.")
                    st.session_state.results['rangeability_status'] = f"Acceptable ({opening_percent:.1f}% open)"
            except Exception as e:
                st.warning(f"Could not perform rangeability analysis. Error: {e}")
    except Exception as e:
        st.error(f"An error occurred during calculation: {e}")
        st.warning("Please go back and check your input values.")
    col1, col2 = st.columns([1,5])
    with col1: st.button("⬅️ Back to Step 2", on_click=prev_step)
    with col2: st.button("Continue to Noise Calculation ➡️", on_click=next_step)

# --- STEP 4: Noise Prediction ---
elif st.session_state.step == 4:
    st.header("Step 4: Noise Prediction (IEC 60534-8-3 Model)")
    try:
        noise_results = noise_prediction.predict_noise(st.session_state.input_data, st.session_state.results)
        st.session_state.results.update(noise_results)
        st.metric("Predicted Noise Level (at 1m)", f"{noise_results['total_noise_dba']:.1f} dBA")
        if noise_results['total_noise_dba'] > 85:
            st.error("High Noise Alert! Level exceeds 85 dBA, which may require hearing protection and specialized equipment.")
            st.warning(f"**Recommendation:** {noise_results['noise_recommendation']}")
        else:
            st.success("Noise level is within acceptable limits (< 85 dBA).")
    except Exception as e:
        st.error(f"An error occurred during noise prediction: {e}")
    col1, col2 = st.columns([1,5])
    with col1: st.button("⬅️ Back to Step 3", on_click=prev_step)
    with col2: st.button("Continue to Actuator & Material Selection ➡️", on_click=next_step)
        
# --- STEP 5: Actuator, Materials & Final Selection ---
elif st.session_state.step == 5:
    st.header("Step 5: Actuator, Materials, and Final Selection")
    with st.expander("Actuator Sizing", expanded=True):
        fail_position = st.radio("Fail-Safe Position", ["Fail Close (FC)", "Fail Open (FO)"], horizontal=True, help="The position the valve should move to on loss of power/air.")
        st.session_state.input_data['fail_position'] = fail_position
        actuator_results = actuator_sizing.size_actuator(st.session_state.input_data, st.session_state.results)
        st.session_state.results.update(actuator_results)
        if st.session_state.input_data['valve_type'] == 'Globe':
            st.metric("Required Actuator Thrust", f"{actuator_results['required_force']:.2f} {units['force']}")
        else:
            st.metric("Required Actuator Torque", f"{actuator_results['required_torque']:.2f} {units['torque']}")
        st.info(f"**Recommendation:** {actuator_results['actuator_recommendation']}")
    with st.expander("Material Selection", expanded=True):
        material_results = materials.select_materials(st.session_state.input_data)
        st.session_state.results.update(material_results)
        st.write("**Recommended Materials:**")
        df_materials = pd.DataFrame([material_results['recommendations']])
        st.table(df_materials)
        st.success(f"**Compliance Check:** {material_results['compliance_check']}")
    with st.expander("Valve Dynamic Characteristic Curve", expanded=True):
        fig = helpers.plot_valve_characteristic(st.session_state.input_data, st.session_state.results['cv'])
        st.plotly_chart(fig, use_container_width=True)
        try:
            img_bytes = fig.to_image(format="png", width=800, height=400, scale=2)
            st.session_state.results['plot_image_bytes'] = img_bytes
        except Exception as e:
            st.warning(f"Could not generate plot image for report: {e}")
            st.session_state.results['plot_image_bytes'] = None
    col1, col2 = st.columns([1,5])
    with col1: st.button("⬅️ Back to Step 4", on_click=prev_step)
    with col2: st.button("Finalize and Generate Report ➡️", on_click=next_step)

# --- STEP 6: Summary and Report Generation ---
elif st.session_state.step == 6:
    st.header("Step 6: Summary and Report")
    st.subheader("Calculation Summary")
    with st.expander("View Full Input and Result Data", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Process Inputs:**")
            st.json({k: v for k, v in st.session_state.input_data.items() if k not in ['units']})
        with col2:
            st.write("**Sizing Results:**")
            st.json({k: v for k, v in st.session_state.results.items() if k != 'plot_image_bytes'})
    st.success("Valve sizing and selection is complete. You can now generate a formal report.")
    st.subheader("Generate PDF Report")
    st.info("Click the button below to generate a detailed PDF report of the valve sizing calculation.")
    report_data = {
        "inputs": st.session_state.input_data,
        "results": st.session_state.results,
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Correctly unpack the tuple (filename, data) returned by the function
    pdf_filename, pdf_bytes = pdf_generator.create_pdf_report(report_data)
    
    st.download_button(
        label="📥 Download PDF Report", 
        data=pdf_bytes, 
        file_name=pdf_filename, 
        mime="application/pdf"
    )
    st.button("⬅️ Back to Step 5", on_click=prev_step)
