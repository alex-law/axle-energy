# TODO: this file returns dummy data: everything should be replaced by calls to your logic
# Feel free to implement your logic within this process, or make calls to an external service

import streamlit as st

from models import ChargerState, DemoAdminState, CombinedState
from utils import get_scheduled_override


def get_future_states() -> list[CombinedState]:
    """Return a list of future states for the system. This is used for plotting the charge trajectory."""
    # TODO: replace this with your logic
    return []


def get_car_state(demo_state: DemoAdminState) -> ChargerState:
    # TODO: replace this with your logic. Feel free to rewrite to combine with the function above if necessary.
    # When you're done, we shouldn't have these toggles in the frontend; they should be determined by the backend.
    with st.sidebar:
        car_is_charging = st.toggle(
            "Currently Charging", value=True, disabled=not demo_state.car_is_plugged_in
        )
        charge_is_override = st.toggle(
            "Charging is Override", value=True, disabled=not demo_state.car_is_plugged_in
        )

    return ChargerState(
        car_is_charging=car_is_charging, charge_is_override=charge_is_override
    )


def button_control(car_is_plugged_in: bool) -> None:
    car_is_charging, charge_is_override = get_scheduled_override()

    st.subheader("Controls")
    c1, c2 = st.columns([1, 1])

    # Not plugged in scenario
    if not car_is_plugged_in:
        scheduled_text = "Start scheduled Charging"
        override_text = "Start override"
        return (
            c1.button(scheduled_text, disabled=True, on_click=handle_scheduled_charge),
            c2.button(override_text, disabled=True, on_click=handle_override_charge),
        )
    
    # Plugged in scenarios
    else:

        # No schedule, No override scenario (D from notes)
        if not car_is_charging and not charge_is_override:
            scheduled_text = "Start scheduled Charging"
            override_text = "Start override"
            return (
                c1.button(scheduled_text, disabled=False, on_click=handle_scheduled_charge),
                c2.button(override_text, disabled=True, on_click=handle_override_charge),
            )

        # Yes schedule, No override scenario (B from notes) 
        elif car_is_charging and not charge_is_override:
            scheduled_text = "Stop scheduled Charging for specific time: "
            override_text = "Start override up to %: "
            return (
                c1.button(scheduled_text, disabled=False, on_click=handle_scheduled_charge),
                c2.button(override_text, disabled=False, on_click=handle_override_charge),
            )

        # Yes schedule, Yes override scenario (A from notes)
        elif car_is_charging and charge_is_override:
            scheduled_text = "Stop scheduled Charging"
            override_text = "Stop override"
            return (
                c1.button(scheduled_text, disabled=True, on_click=handle_scheduled_charge),
                c2.button(override_text, disabled=False, on_click=handle_override_charge),
            )

        # No schedule, Yes override scenario (C from notes) 
        else:
            raise Exception(f"Schedule: {car_is_charging}, Override: {charge_is_override}.\nThis scenario should not be possible")    


def handle_scheduled_charge() -> None:
    # TODO add docstring
    # Should only affect car_is_charging from car_state
    car_is_charging, charge_is_override = get_scheduled_override()
    if car_is_charging and not charge_is_override:
        st.session_state['car_state'].car_is_charging = False
        st.toast("Stoping scheduled charge", icon="⚠️")
    elif not car_is_charging and not charge_is_override:
        st.session_state['car_state'].car_is_charging = True
        st.toast("Starting scheduled charge", icon="🚀")
    # No other combinations should make it this far
    else:
        raise Exception('Invalid scheduled override combo')

def handle_override_charge() -> None:
    # TODO add docstring
    # Should only affect charge_is_override from car_state
    car_is_charging, charge_is_override = get_scheduled_override()
    if car_is_charging and charge_is_override:
        st.session_state['car_state'].charge_is_override = False
        st.toast("Stopping override", icon="🛑")
    elif car_is_charging and not charge_is_override:
        st.session_state['car_state'].charge_is_override = True
        st.toast("Starting override", icon="🔥")
    # No other combinations should make it this far
    else:
        raise Exception('Invalid scheduled override combo')