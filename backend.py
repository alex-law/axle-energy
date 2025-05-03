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


def handle_scheduled_charge():
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

def handle_override_charge():
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