import math
from datetime import timedelta

velocity_cache = {}

# Checks or Keeps Track how fast transactions arrive in memory 
def check_velocity(user_id, current_time):
    if user_id not in velocity_cache:
        velocity_cache[user_id] = []
    velocity_cache[user_id].append(current_time)
    cutoff_time = current_time - timedelta(seconds=60)

    recent_timestamps = []
    for timestamp in velocity_cache[user_id]:
        if timestamp > cutoff_time:
            recent_timestamps.append(timestamp)

    velocity_cache[user_id] = recent_timestamps


    return len(velocity_cache[user_id]) > 5


# Z-Score Function
def check_outlier(history_list, new_amount):
    if len(history_list) < 3:
        return False

    mean = sum(history_list) / len(history_list)

    variance_sum = 0

    for amount in history_list:
        variance_sum = variance_sum + ((mean - amount) ** 2 )

    variance = variance_sum / len(history_list)

    std_dev = math.sqrt(variance)
    if std_dev == 0:
        std_dev = 1

    z_score = (new_amount - mean) / std_dev

    return abs(z_score) > 3.0
        