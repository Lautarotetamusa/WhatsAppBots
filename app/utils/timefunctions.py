from datetime import datetime, date, timedelta
from home import settings
import pytz

def parse_time(time):
    #convertimos el objeto time -> datetime con la fecha de hoy
    local_dt = datetime.combine(date.today(), time)

    #pasar de la hora seteada en Local time zone a una hora en UTC
    tz = pytz.timezone(settings.LOCAL_TIME_ZONE)
    dt = tz.localize(local_dt)
    return dt.astimezone(pytz.UTC)
