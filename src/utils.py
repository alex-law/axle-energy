from datetime import datetime, timedelta
import streamlit as st

from models import BatteryState

def get_current_time_to_nearest_30_minutes(current_time: datetime.time):
    """Return the current time, rounded to the nearest 30 minutes"""
    minutes = 30 * round(current_time.minute / 30)
    rounded_date = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)
    return rounded_date.time()


def add_period_to_rounded_time(rounded_time, period):
    dummy_date = datetime.now().date()
    start_datetime = datetime.combine(dummy_date, rounded_time)
    end_datetime = start_datetime + period
    return end_datetime.time()


def get_scheduled_override() -> tuple[bool, bool]:
    """Get car_is_charging and charge_is_override variables from st session_state"""
    car_is_charging = st.session_state['charger_state'].car_is_charging
    charge_is_override = st.session_state['charger_state'].charge_is_override
    return car_is_charging, charge_is_override


def battery_indicator(battery_state: BatteryState):
    """Generates HTML for a battery indicator with a percentage bar."""
    # Could use something like psutil to get live indication of battery level
    # but feel that is too complicated for this demo
    
    percentage = int(battery_state.soc*100)
    color = "#4CAF50" if percentage > 50 else "#FFC107" if percentage > 20 else "#F44336"
    charge_status = "Charging" if st.session_state['charger_state'].car_is_charging else ""

    # TODO add in bit for override

    html = f"""
    <div style="
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    ">
        <p style="margin-bottom: 5px; font-weight: bold;">{charge_status}</p>
        <div style="
            background-color: #ddd;
            border-radius: 3px;
            height: 20px;
            width: 100%;
            overflow: hidden;
        ">
            <div style="
                background-color: {color};
                height: 100%;
                width: {percentage}%;
                border-radius: 3px;
                text-align: center;
                color: white;
                line-height: 20px;
                font-size: 12px;
            ">
                {percentage}%
            </div>
        </div>
    </div>
    """
    return html

