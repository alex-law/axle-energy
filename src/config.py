from datetime import time, timedelta

# Set the resampling period for graphing
PERIOD = timedelta(minutes=30)
# How many period steps to show in graph
RANGE_STEPS = 9
# Start time for low price
LOW_PRICE_START_TIME = time(2, 0)
# How long should default low price be
LOW_PRICE_DURATION = 3
# How fast does the battery charge 0.1 soc / 1hr
CHARGE_RATE = 0.1