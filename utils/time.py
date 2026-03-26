import swisseph as swe

def to_julian(year, month, day, hour, minute):
    decimal_hour = hour + (minute / 60)
    jd = swe.julday(year, month, day, decimal_hour)
    return jd