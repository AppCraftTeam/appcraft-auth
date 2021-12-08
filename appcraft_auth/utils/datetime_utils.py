import datetime

import pytz
from django.utils.timezone import make_aware, get_current_timezone, localtime


def timestamp_to_datetime(timestamp, local_time=True, milliseconds=True):
    delta = datetime.timedelta(milliseconds=timestamp) if milliseconds else datetime.timedelta(seconds=timestamp)
    if local_time:
        tz = get_current_timezone()
        overflowed_date = make_aware(
            datetime.datetime(1970, 1, 1) + delta, pytz.timezone("UTC")
        )
        overflowed_date = localtime(overflowed_date, tz)
    else:
        overflowed_date = make_aware(
            datetime.datetime(1970, 1, 1) + delta, pytz.timezone("UTC")
        )
    return overflowed_date
