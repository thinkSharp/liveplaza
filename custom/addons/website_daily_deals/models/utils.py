from datetime import datetime
from pytz import timezone


def today_myanmar_time():
  tz = timezone('Asia/Yangon')
  now = datetime.now(tz)
  return now.date()
