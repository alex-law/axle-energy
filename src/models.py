from dataclasses import dataclass
from datetime import datetime, time


@dataclass
class BatteryState:
    """The state of the battery"""
    # Setting up seperate dataclass for this since in actual prod code
    # base likely to have a lot more variables associated with it other 
    # than just soc and charge rate

    # Keeping battery storage ratio as soc in backend since
    # seems compatible with what you guys use
    soc: float
    charge_rate: float

@dataclass
class DemoAdminState:
    """State we control from the admin panel to control the demo"""

    car_is_plugged_in: bool
    low_price_start: time
    low_price_end: time
    current_time: datetime
    battery_state: BatteryState

@dataclass
class ChargerState:
    """State of the car's charger"""

    car_is_charging: bool
    charge_is_override: bool
    desired_soc: float


@dataclass
class CombinedState:
    """Helper class for grouping battery & charger data together"""

    time: datetime
    charger_state: ChargerState
