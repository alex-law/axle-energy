# TODO: this file returns dummy data: everything should be replaced by calls to your logic
# Feel free to implement your logic within this process, or make calls to an external service

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, time

from models import  CombinedState, BatteryState
from utils import (
    get_scheduled_override,
    add_period_to_rounded_time
)

# TODO link with period data etc in plotting
PERIOD = timedelta(minutes=30)
RANGE_STEPS = 20


def get_scheduled_times():
    # Going to the extra effort of getting date and time to avoid confusion around midnight
    # today = datetime.now()
    schedule_start_time = time(2, 0, 0)
    # schedule_start_date = datetime.combine(today.date(), schedule_start_time)
    schedule_end_time = time(5, 0, 0)
    # schedule_end_date = datetime.combine(today.date(), schedule_end_time)
    return schedule_start_time, schedule_end_time


def get_future_states(battery_state: BatteryState, current_time: datetime.time) -> pd.DataFrame:
    """Return a list of future states for the system. This is used for plotting the charge trajectory."""
    soc = battery_state.soc
    car_is_charging, charge_is_override = get_scheduled_override()
    desired_soc = st.session_state['charger_state'].desired_soc

    schedule_start_time, schedule_end_time = get_scheduled_times()

    # TODO refactor to move charging override logic into seperate functions, add to notes
    # TODO maybe allow scheduled time to be set in demo admin controls
    # TODO overshoot on override

    dicts_for_df = []
    if charge_is_override:
        for i in range(RANGE_STEPS):
            # If rounded time during scheduled time
            if schedule_start_time <= current_time < schedule_end_time:
                override = False
                if soc <= 1:
                    charging = True
                else:
                    charging = False
                # If not during scheduled time
            else:
                # If less than desired soc then overide
                if soc < desired_soc:
                    charging = True
                    override = True
                else:
                    charging = False
                    override = False

            data_dict = {
                'Time': current_time,
                'Battery %': int(soc*100),
                'Car is Charging': charging,
                'Charge is Override': override
            }
            current_time = add_period_to_rounded_time(current_time, PERIOD)
            if charging:
                soc += battery_state.charge_rate
                soc = min(1, soc, desired_soc)
            dicts_for_df.append(data_dict)

    elif car_is_charging and not charge_is_override:
        override = False
        for i in range(RANGE_STEPS):
            if (schedule_start_time <= current_time < schedule_end_time) and (soc <= 1):
                charging = True
            else:
                charging = False

            data_dict = {
                'Time': current_time,
                'Battery %': int(soc*100),
                'Car is Charging': charging,
                'Charge is Override': override
            }
            current_time = add_period_to_rounded_time(current_time, PERIOD)
            if charging:
                soc += battery_state.charge_rate
                soc = min(1, soc)
            dicts_for_df.append(data_dict)

    elif not car_is_charging:
        for i in range(RANGE_STEPS):
            data_dict = {
                    'Time': current_time,
                    'Battery %': int(soc*100),
                    'Car is Charging': False,
                    'Charge is Override': False
                }
            current_time = add_period_to_rounded_time(current_time, PERIOD)
            dicts_for_df.append(data_dict)

    else:
        raise Exception('Unnacounted for charging scenario')

    df = pd.DataFrame(dicts_for_df)

    return df

# TODO now position not working, want graph to update x axis range when time changes

def button_control(car_is_plugged_in: bool, soc: float):
    
    car_is_charging, charge_is_override = get_scheduled_override()

    st.subheader("Controls")
    
    #TODO split scenarios into functions

    # Not plugged in scenario
    if not car_is_plugged_in:
        c1, c2 = st.columns([1, 1])
        scheduled_text = "Plug in to start scheduled charging"
        override_text = "Plug in to start override"
        c1.button(scheduled_text, disabled=True, on_click=handle_scheduled_charge)
        c2.button(override_text, disabled=True, on_click=handle_override_charge)
    
    
    # Plugged in scenarios
    else:

        # No schedule, No override scenario (D from notes)
        if not car_is_charging and not charge_is_override:
            c1, c2 = st.columns([1, 1])
            scheduled_text = "Start scheduled charging"
            override_text = "Start override"
            c1.button(scheduled_text, disabled=False, on_click=handle_scheduled_charge)
            c2.button(override_text, disabled=True, on_click=handle_override_charge)

        # TODO need to enter charge percentage before clicking on start overide

        # Yes schedule, No override scenario (B from notes) 
        elif car_is_charging and not charge_is_override:
            c1_row1, c2_row1 = st.columns([1, 1])
            # If we need to get desired percentage chart then add in extra input for this
            desired_percentage_input = c2_row1.number_input(
                "Override charge up to %",
                min_value=int(soc*100),
                max_value=100,
                step=1,
                help="Enter Battery %"
            )
            st.session_state['charger_state'].desired_soc = desired_percentage_input / 100.0

            c1_row2, c2_row2 = st.columns([1, 1])
            scheduled_text = "Stop scheduled charging for specific time: "
            override_text = "Start override"
       
            c1_row2.button(scheduled_text, disabled=False, on_click=handle_scheduled_charge)
            c2_row2.button(override_text, disabled=False, on_click=handle_override_charge)

        # Yes schedule, Yes override scenario (A from notes)
        elif car_is_charging and charge_is_override:
            c1, c2 = st.columns([1, 1])
            scheduled_text = "Stop scheduled charging"
            override_text = "Stop override"
            c1.button(scheduled_text, disabled=True, on_click=handle_scheduled_charge)
            c2.button(override_text, disabled=False, on_click=handle_override_charge)

        # No schedule, Yes override scenario (C from notes) 
        else:
            raise Exception(f"Schedule: {car_is_charging}, Override: {charge_is_override}.\nThis scenario should not be possible")    


def handle_scheduled_charge() -> None:
    # TODO add docstring
    # Should only affect car_is_charging from charger_state
    car_is_charging, charge_is_override = get_scheduled_override()
    if car_is_charging and not charge_is_override:
        st.session_state['charger_state'].car_is_charging = False
        st.toast("Stoping scheduled charge", icon="⚠️")
    elif not car_is_charging and not charge_is_override:
        st.session_state['charger_state'].car_is_charging = True
        st.toast("Starting scheduled charge", icon="🚀")
    # No other combinations should make it this far
    else:
        raise Exception('Invalid scheduled override combo')

def handle_override_charge() -> None:
    # TODO add docstring
    # Should only affect charge_is_override from charger_state
    car_is_charging, charge_is_override = get_scheduled_override()
    if car_is_charging and charge_is_override:
        st.session_state['charger_state'].charge_is_override = False
        st.toast("Stopping override", icon="🛑")
    elif car_is_charging and not charge_is_override:
        st.session_state['charger_state'].charge_is_override = True
        st.toast("Starting override", icon="🔥")
    # No other combinations should make it this far
    else:
        raise Exception('Invalid scheduled override combo')