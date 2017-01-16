
def get_time_in_seconds(interval, interval_unit):
    if interval_unit.lower() == 'weeks':
        return interval * 7 * 24 * 60 * 60
    elif interval_unit.lower() == 'days':
        return interval * 24 * 60 * 60
    elif interval_unit.lower() == 'hours':
        return interval * 60 * 60
    elif interval_unit.lower() == 'minutes':
        return interval * 60
    elif interval_unit.lower() == 'seconds':
        return interval
