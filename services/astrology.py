import swisseph as swe

# Set ephemeris path
swe.set_ephe_path('./ephe')

PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
    "rahu": swe.MEAN_NODE,
    "ketu": swe.MEAN_NODE
}

def calculate_planets(jd):
    result = {}

    for name, planet in PLANETS.items():
        pos = swe.calc_ut(jd, planet)[0]

        result[name] = {
            "longitude": pos[0],
            "latitude": pos[1],
            "distance": pos[2]
        }

    return result