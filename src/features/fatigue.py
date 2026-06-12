import math


HOST_CITIES = {
    "Mexico": "Mexico City",
    "Canada": "Toronto",
    "USA": "New York",
    "Argentina": "Buenos Aires",
    "Brazil": "Brasilia",
    "England": "London",
    "France": "Paris",
    "Germany": "Berlin",
    "Spain": "Madrid",
    "Netherlands": "Amsterdam",
    "Portugal": "Lisbon",
    "Croatia": "Zagreb",
    "Belgium": "Brussels",
    "Switzerland": "Bern",
    "Italy": "Rome",
    "Uruguay": "Montevideo",
    "Colombia": "Bogota",
    "Japan": "Tokyo",
    "South Korea": "Seoul",
    "Australia": "Sydney",
    "Iran": "Tehran",
    "Saudi Arabia": "Riyadh",
    "Morocco": "Rabat",
    "Senegal": "Dakar",
    "Egypt": "Cairo",
    "Ghana": "Accra",
    "Tunisia": "Tunis",
    "Nigeria": "Abuja",
    "Cameroon": "Yaounde",
    "New Zealand": "Wellington",
    "Sweden": "Stockholm",
    "Norway": "Oslo",
    "Scotland": "Glasgow",
    "Austria": "Vienna",
    "Poland": "Warsaw",
    "Turkey": "Ankara",
    "Czechia": "Prague",
    "Paraguay": "Asuncion",
    "Ecuador": "Quito",
    "Iraq": "Baghdad",
    "Jordan": "Amman",
    "Uzbekistan": "Tashkent",
    "Cape Verde": "Praia",
    "Algeria": "Algiers",
    "Ivory Coast": "Yamoussoukro",
    "South Africa": "Pretoria",
    "Panama": "Panama City",
    "Haiti": "Port-au-Prince",
    "Curacao": "Willemstad",
    "DR Congo": "Kinshasa",
    "Bosnia and Herzegovina": "Sarajevo",
    "Qatar": "Doha",
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


COORDS = {
    "Mexico City": (19.4326, -99.1332),
    "Toronto": (43.6532, -79.3832),
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Dallas": (32.7767, -96.7970),
    "Houston": (29.7604, -95.3698),
    "Atlanta": (33.7490, -84.3880),
    "Boston": (42.3601, -71.0589),
    "Philadelphia": (39.9526, -75.1652),
    "Seattle": (47.6062, -122.3321),
    "San Francisco": (37.7749, -122.4194),
    "Miami": (25.7617, -80.1918),
    "Kansas City": (39.0997, -94.5786),
    "Monterrey": (25.6866, -100.3161),
    "Guadalajara": (20.6597, -103.3496),
    "Vancouver": (49.2827, -123.1207),
}


class FatigueAnalyzer:
    def compute_rest_days(self, match_date: str, prev_match_date: str = None) -> int:
        if not prev_match_date:
            return 7
        from datetime import datetime
        d1 = datetime.strptime(match_date, "%Y-%m-%d")
        d2 = datetime.strptime(prev_match_date, "%Y-%m-%d")
        return (d1 - d2).days

    def compute_travel_distance(self, team: str, match_location: str) -> float:
        home_city = HOST_CITIES.get(team)
        if not home_city or match_location not in COORDS:
            return 0
        home_coords = COORDS.get(home_city)
        match_coords = COORDS.get(match_location)
        if not home_coords or not match_coords:
            return 0
        return haversine_km(*home_coords, *match_coords)

    def compute_all(self, team: str, match_date: str, match_location: str = "New York",
                    prev_match_date: str = None) -> dict:
        rest_days = self.compute_rest_days(match_date, prev_match_date)
        travel_km = self.compute_travel_distance(team, match_location)
        return {
            "rest_days": rest_days,
            "travel_distance_km": round(travel_km, 0),
            "is_short_rest": rest_days < 3,
            "is_long_travel": travel_km > 5000,
            "fatigue_index": round(
                (max(0, 3 - rest_days) / 3 * 0.5 + min(travel_km / 10000, 1) * 0.5), 3
            ),
        }
