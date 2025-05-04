import streamlit as st

import backend
from models import DemoAdminState, BatteryState, ChargerState
from plotting import plot_upcoming_charges
from utils import ( 
    get_current_time_to_nearest_30_minutes,
    battery_indicator,
    get_scheduled_override
)


def get_demo_state() -> DemoAdminState:
    rounded_time = get_current_time_to_nearest_30_minutes()
    with st.sidebar:
        st.subheader("Demo Admin Controls")
        st.write("Use these controls to simulate the car and charger state.")

        percentage_input = st.number_input(
            "Battery %",
            min_value=0,
            max_value=100,
            step=1,
            help="Enter Battery %"
        )
        soc = percentage_input / 100.0

        # This is used to create the select time drop down
        current_time = st.time_input("Current Time", rounded_time)
        # When creating st current time, hour and minute aren't automatically
        # included, so need to add back in from datetime object here
        current_time = rounded_time.replace(
            hour=current_time.hour, minute=current_time.minute
        )

        car_is_plugged_in = st.toggle("Plugged in", value=True)

    # Hardcoding charge rate as 0.1 soc / 1hr
    charge_rate = 0.1

    return DemoAdminState(
        car_is_plugged_in=car_is_plugged_in,
        current_time=current_time,
        battery_state=BatteryState(soc=soc, charge_rate=charge_rate)
    )


if __name__ == "__main__":
    # Not setting demo_state to be a session state since should only be changed during initial set up
    if 'initial_load' not in st.session_state:
        st.session_state['initial_load'] = True
        demo_state = get_demo_state()
        # Charging states need to start off with a value so just set both to false here
        st.session_state['charger_state'] = ChargerState(car_is_charging=False, charge_is_override=False, desired_soc=1.0)
    else:
        demo_state = get_demo_state()
        # If demo mode has been reset to have car not plugged in then reset charging and override to false
        if not demo_state.car_is_plugged_in:
            st.session_state['charger_state'] = ChargerState(car_is_charging=False, charge_is_override=False, desired_soc=1.0)
        st.session_state['initial_load'] = False
    # Display battery percentage
    battery_placeholder = st.empty()
    battery_html = battery_indicator(demo_state.battery_state)
    battery_placeholder.markdown(battery_html, unsafe_allow_html=True)

    st.subheader("Charging Schedule")

    df_plot = backend.get_future_states(demo_state.battery_state, demo_state.current_time)

    st.plotly_chart(
        plot_upcoming_charges(
            df_plot,
            current_time=demo_state.current_time,
        )
    )

    car_is_charging, charge_is_override = get_scheduled_override()


    backend.button_control(
        demo_state.car_is_plugged_in,
        demo_state.battery_state.soc
    )
