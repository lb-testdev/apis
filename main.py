from fastapi import FastAPI, Query, HTTPException
import swisseph as swe
from datetime import datetime
from zoneinfo import ZoneInfo

app = FastAPI(title="Astrology API (Vedic Correct)", version="3.0.0")

# 🔹 Setup
swe.set_ephe_path('./ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)

FLAGS = swe.FLG_SIDEREAL

PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
    "rahu": swe.MEAN_NODE
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# 🔹 Julian
def to_julian(year, month, day, hour, minute):
    # IST datetime
    dt_ist = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("Asia/Kolkata"))

    # Convert to UTC
    dt_utc = dt_ist.astimezone(ZoneInfo("UTC"))

    # Decimal hour
    hour_decimal = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600

    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        hour_decimal
    )

# 🔹 Rashi
def get_rashi(longitude):
    return int(longitude // 30)

# 🔹 Calculate planets
def calculate_planets(jd):
    data = {}

    for name, planet in PLANETS.items():
        pos = swe.calc_ut(jd, planet, FLAGS)[0]
        lon = pos[0] % 360

        data[name] = {
            "longitude": round(lon, 4),
            "rashi_index": get_rashi(lon),
            "rashi": SIGNS[get_rashi(lon)]
        }

    # Ketu
    rahu_lon = data["rahu"]["longitude"]
    ketu_lon = (rahu_lon + 180) % 360

    data["ketu"] = {
        "longitude": round(ketu_lon, 4),
        "rashi_index": get_rashi(ketu_lon),
        "rashi": SIGNS[get_rashi(ketu_lon)]
    }

    return data

# 🔹 Ascendant
def calculate_ascendant(jd, lat, lon):
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', FLAGS)
    asc = ascmc[0] % 360
    return asc, get_rashi(asc)

# 🔹 Whole Sign Houses (IMPORTANT)
def build_whole_sign_houses(asc_rashi):
    houses = {}

    for i in range(12):
        house_num = i + 1
        sign_index = (asc_rashi + i) % 12

        houses[house_num] = {
            "rashi": SIGNS[sign_index],
            "rashi_index": sign_index,
            "planets": []
        }

    return houses

# 🔹 Assign planets to houses
def assign_planets_to_houses(planets, houses, asc_rashi):
    for planet, data in planets.items():
        planet_sign = data["rashi_index"]

        house_number = ((planet_sign - asc_rashi) % 12) + 1

        houses[house_number]["planets"].append(planet.upper())

    return houses

# 🔥 MAIN API
@app.get("/kundli")
def get_kundli(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lon: float
):
    try:
        datetime(year, month, day, hour, minute)

        jd = to_julian(year, month, day, hour, minute)

        swe.set_topo(lon, lat, 0)

        planets = calculate_planets(jd)

        asc_degree, asc_rashi = calculate_ascendant(jd, lat, lon)

        houses = build_whole_sign_houses(asc_rashi)

        houses = assign_planets_to_houses(planets, houses, asc_rashi)

        return {
            "ascendant": {
                "degree": round(asc_degree, 4),
                "rashi": SIGNS[asc_rashi]
            },
            "zodiac": "sidereal (lahiri)",
            "planets": planets,
            "houses": houses
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))