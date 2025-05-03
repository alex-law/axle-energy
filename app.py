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

    return DemoAdminState(
        car_is_plugged_in=car_is_plugged_in,
        current_time=current_time,
        battery_state=BatteryState(soc=soc)
    )


def controls(car_is_plugged_in: bool):

    # TODO want to move this to backend scripts

    car_is_charging, charge_is_override = get_scheduled_override()

    st.subheader("Controls")
    c1, c2 = st.columns([1, 1])

    # Not plugged in scenario

    # TODO add in something to say need to plug in first

    if not car_is_plugged_in:
        scheduled_text = "Start scheduled Charging"
        override_text = "Start override"
        return (
            c1.button(scheduled_text, disabled=True, on_click=backend.handle_scheduled_charge),
            c2.button(override_text, disabled=True, on_click=backend.handle_override_charge),
        )
    
    # Plugged in scenarios
    else:

        # No schedule, No override scenario (D from notes)
        if not car_is_charging and not charge_is_override:
            scheduled_text = "Start scheduled Charging"
            override_text = "Start override"
            return (
                c1.button(scheduled_text, disabled=False, on_click=backend.handle_scheduled_charge),
                c2.button(override_text, disabled=True, on_click=backend.handle_override_charge),
            )

        # Yes schedule, No override scenario (B from notes) 
        elif car_is_charging and not charge_is_override:
            scheduled_text = "Stop scheduled Charging for specific time: "
            override_text = "Start override up to %: "
            return (
                c1.button(scheduled_text, disabled=False, on_click=backend.handle_scheduled_charge),
                c2.button(override_text, disabled=False, on_click=backend.handle_override_charge),
            )

        # Yes schedule, Yes override scenario (A from notes)
        elif car_is_charging and charge_is_override:
            scheduled_text = "Stop scheduled Charging"
            override_text = "Stop override"
            return (
                c1.button(scheduled_text, disabled=True, on_click=backend.handle_scheduled_charge),
                c2.button(override_text, disabled=False, on_click=backend.handle_override_charge),
            )

        # No schedule, Yes override scenario (C from notes) 
        else:
            raise Exception(f"Schedule: {car_is_charging}, Override: {charge_is_override}.\nThis scenario should not be possible")    


if __name__ == "__main__":
    # Not setting demo_state to be a session state since should only be changed during initial set up
    if 'initial_load' not in st.session_state:
        st.session_state['initial_load'] = True
        demo_state = get_demo_state()
        # Charging states need to start off with a value so just set both to false here
        st.session_state['car_state'] = ChargerState(car_is_charging=False, charge_is_override=False)
    else:
        demo_state = get_demo_state()
        # If demo mode has been reset to have car not plugged in then reset charging and override to false
        if not demo_state.car_is_plugged_in:
            st.session_state['car_state'] = ChargerState(car_is_charging=False, charge_is_override=False)
        st.session_state['initial_load'] = False
    # Display battery percentage
    battery_placeholder = st.empty()
    battery_html = battery_indicator(demo_state.battery_state)
    battery_placeholder.markdown(battery_html, unsafe_allow_html=True)

    st.subheader("Charging Schedule")

    st.plotly_chart(
        plot_upcoming_charges(
            backend.get_future_states(),
            current_time=demo_state.current_time,
        )
    )
    start_charging, stop_charging = controls(demo_state.car_is_plugged_in)
