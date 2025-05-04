from datetime import timedelta, time
import streamlit as st

import backend
from config import LOW_PRICE_START_TIME, LOW_PRICE_DURATION, CHARGE_RATE
from models import DemoAdminState, BatteryState, ChargerState
from plotting import plot_upcoming_charges
from utils import ( 
    get_current_time_to_nearest_30_minutes,
    battery_indicator,
    add_period_to_rounded_time
)


def set_start_end_low_price() -> tuple[time, time]:
    """
    Make default start and end low price times seinsible to encourage
    always having end time later than start time
    """
    if 'low_price_start_limit' in st.session_state:
        low_price_start_limit = st.session_state['low_price_start_limit']
    else:
        low_price_start_limit = LOW_PRICE_START_TIME
    low_price_start = st.time_input('Low Price Start Time', low_price_start_limit)
    low_price_end_limit = add_period_to_rounded_time(low_price_start, timedelta(hours=LOW_PRICE_DURATION))
    low_price_end = st.time_input('Low Price End Time', low_price_end_limit)
    st.session_state['low_price_start_limit'] = add_period_to_rounded_time(low_price_end_limit, timedelta(hours=21))
    return low_price_start, low_price_end


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
        current_time = st.time_input("Current Time", rounded_time)
        low_price_start, low_price_end = set_start_end_low_price()
        car_is_plugged_in = st.toggle("Plugged in", value=True)

    return DemoAdminState(
        car_is_plugged_in=car_is_plugged_in,
        low_price_start=low_price_start,
        low_price_end=low_price_end,
        current_time=current_time,
        battery_state=BatteryState(soc=soc, charge_rate=CHARGE_RATE)
    )


def main(demo_state):
    """
    Main function to handle charging app
    """
    # Display battery percentage
    battery_placeholder = st.empty()
    battery_html = battery_indicator(demo_state.battery_state)
    battery_placeholder.markdown(battery_html, unsafe_allow_html=True)

    # Plot graph
    st.subheader("Charging Schedule")
    df_plot = backend.get_future_states(demo_state)
    st.plotly_chart(
        plot_upcoming_charges(
            df_plot,
            current_time=demo_state.current_time,
        )
    )

    # Display control buttons
    backend.button_control(
        demo_state.car_is_plugged_in,
        demo_state.battery_state.soc
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

    main(demo_state)
    
