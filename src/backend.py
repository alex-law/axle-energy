import pandas as pd
import streamlit as st
from datetime import time

from models import  DemoAdminState
from config import PERIOD, RANGE_STEPS
from utils import (
    get_scheduled_override,
    add_period_to_rounded_time
)


def get_override_charge_dicts(
        soc: float,
        current_time: time,
        schedule_start_time: time,
        schedule_end_time: time,
        desired_soc: float,
        charge_rate: float
    ) -> list:
    dicts_for_df = []
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
            soc += charge_rate
            soc = min(1, soc)
        dicts_for_df.append(data_dict)
    return dicts_for_df


def get_standard_charge_dicts(
        soc: float,
        current_time: time,
        schedule_start_time: time,
        schedule_end_time: time,
        charge_rate: float
    ) -> list:
    dicts_for_df = []
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
            soc += charge_rate
            soc = min(1, soc)
        dicts_for_df.append(data_dict)
    return dicts_for_df


def get_plot_df(demo_state: DemoAdminState) -> pd.DataFrame:
    """
    Create a dataframe for plotting graph depending on current charging state
    """
    # Set to new variable to prevent demo state changing during graph plot
    soc = demo_state.battery_state.soc
    current_time = demo_state.current_time
    schedule_start_time = demo_state.low_price_start
    schedule_end_time = demo_state.low_price_end
    car_is_charging, charge_is_override = get_scheduled_override()
    desired_soc = st.session_state['charger_state'].desired_soc


    demo_state.battery_state.charge_rate
    if charge_is_override:
        dicts_for_df = get_override_charge_dicts(
            soc,
            current_time,
            schedule_start_time,
            schedule_end_time,
            desired_soc,
            demo_state.battery_state.charge_rate
        )


    elif car_is_charging and not charge_is_override:
        dicts_for_df = get_standard_charge_dicts(
            soc,
            current_time,
            schedule_start_time,
            schedule_end_time,
            demo_state.battery_state.charge_rate
        )

    elif not car_is_charging:
        dicts_for_df = []
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


def not_plugged_in_scenario() -> None:
    c1, c2 = st.columns([1, 1])
    scheduled_text = "Plug in to start scheduled charging"
    override_text = "Plug in to start override"
    c1.button(scheduled_text, disabled=True, on_click=handle_scheduled_charge)
    c2.button(override_text, disabled=True, on_click=handle_override_charge)


def no_override_no_schedule_scenario() -> None:
    c1, c2 = st.columns([1, 1])
    scheduled_text = "Start scheduled charging"
    override_text = "Start override"
    c1.button(scheduled_text, disabled=False, on_click=handle_scheduled_charge)
    c2.button(override_text, disabled=True, on_click=handle_override_charge)


def no_override_yes_schedule_scenario(soc: float) -> None:
    # Two rows and two columns to position override charge above button
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
    # Second row
    c1_row2, c2_row2 = st.columns([1, 1])
    scheduled_text = "Stop scheduled charging"
    c1_row2.button(scheduled_text, disabled=False, on_click=handle_scheduled_charge)
    # Don't want to allow user to click charge if desired soc <= current soc
    if st.session_state['charger_state'].desired_soc <= soc:
        override_text = "Select % to start override"
        c2_row2.button(override_text, disabled=True, on_click=handle_override_charge)
    else:
        override_text = "Start override"
        c2_row2.button(override_text, disabled=False, on_click=handle_override_charge)


def yes_override_yes_schedule_scenario() -> None:
    c1, c2 = st.columns([1, 1])
    scheduled_text = "Stop scheduled charging"
    override_text = "Stop override"
    c1.button(scheduled_text, disabled=True, on_click=handle_scheduled_charge)
    c2.button(override_text, disabled=False, on_click=handle_override_charge)


def button_control(car_is_plugged_in: bool, soc: float) -> None:
    """
    Define button controls depending on current state
    """
    car_is_charging, charge_is_override = get_scheduled_override()
    st.subheader("Controls")
    # Not plugged in scenario
    if not car_is_plugged_in:
        not_plugged_in_scenario()
    # Plugged in scenarios
    else:
        # No schedule, No override scenario (D from notes)
        if not car_is_charging and not charge_is_override:
            no_override_no_schedule_scenario()
        # Yes schedule, No override scenario (B from notes) 
        elif car_is_charging and not charge_is_override:
            no_override_yes_schedule_scenario(soc)
        # Yes schedule, Yes override scenario (A from notes)
        elif car_is_charging and charge_is_override:
            yes_override_yes_schedule_scenario()
        # No schedule, Yes override scenario (C from notes) 
        else:
            raise Exception(f"Schedule: {car_is_charging}, Override: {charge_is_override}.\nThis scenario should not be possible")    


def handle_scheduled_charge() -> None:
    """
    Button with changing content for scheduled charging
    """
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
    """
    Button with changing content for scheduled charging
    """
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