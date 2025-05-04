from datetime import time, timedelta

# Set the resampling period for graphing
PERIOD = timedelta(minutes=30)
# How many period steps to show in graph
RANGE_STEPS = 9
# Start and end time for low price
LOW_PRICE_START_TIME = time(2, 0)
LOW_PRICE_END_TIME = time(5, 0)