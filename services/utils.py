
def get_time_in_seconds(interval, interval_unit):
    if interval_unit == 'Weeks':
        return interval * 7 * 24 * 60 * 60
    elif interval_unit == 'Days':
        return interval * 24 * 60 * 60
    elif interval_unit == 'Hours':
        return interval * 60 * 60
    elif interval_unit == 'Minutes':
        return interval * 60
    elif interval_unit == 'Seconds':
        return interval
