"""FIFA World Cup 2026 fixtures, groups, and teams."""

WC_2026_TEAMS = [
    # Co-hosts
    "Canada", "Mexico", "USA",
    # AFC
    "Australia", "Iran", "Japan", "Jordan", "Qatar", "Saudi Arabia", "South Korea", "Uzbekistan",
    # CAF
    "Algeria", "Cape Verde", "Egypt", "Ghana", "Ivory Coast", "Morocco", "Senegal", "South Africa", "Tunisia",
    # CONCACAF
    "Curacao", "Haiti", "Panama",
    # CONMEBOL
    "Argentina", "Brazil", "Colombia", "Ecuador", "Paraguay", "Uruguay",
    # OFC
    "New Zealand",
    # UEFA
    "Austria", "Belgium", "Bosnia and Herzegovina", "Croatia", "England", "France",
    "Germany", "Netherlands", "Norway", "Portugal", "Scotland", "Spain",
    "Switzerland", "Sweden", "Turkey", "Czechia",
    # Play-off winners
    "DR Congo", "Iraq",
]

WC_2026_GROUPS = {
    "A": ["Mexico", "South Africa", "Paraguay", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Croatia"],
    "C": ["USA", "Turkey", "Algeria", "Sweden"],
    "D": ["Argentina", "Morocco", "Ivory Coast", "Scotland"],
    "E": ["Brazil", "Cape Verde", "Saudi Arabia", "Belgium"],
    "F": ["England", "Iran", "Senegal", "Netherlands"],
    "G": ["France", "Australia", "Tunisia", "Austria"],
    "H": ["Spain", "Japan", "Haiti", "Switzerland"],
    "I": ["Germany", "Ecuador", "Jordan", "Portugal"],
    "J": ["Curacao", "Uruguay", "South Korea", "Panama"],
    "K": ["Colombia", "Egypt", "DR Congo", "Norway"],
    "L": ["New Zealand", "Ghana", "Iraq", "Uzbekistan"],
}

WC_2026_FIXTURES = [
    # Group Stage - Matchdays 1-3 (June 11 - June 27, 2026)
    # Group A
    {"date": "2026-06-11", "home": "Mexico", "away": "South Africa", "group": "A", "stage": "group"},
    {"date": "2026-06-11", "home": "Paraguay", "away": "Czechia", "group": "A", "stage": "group"},
    {"date": "2026-06-15", "home": "Mexico", "away": "Paraguay", "group": "A", "stage": "group"},
    {"date": "2026-06-15", "home": "Czechia", "away": "South Africa", "group": "A", "stage": "group"},
    {"date": "2026-06-19", "home": "Mexico", "away": "Czechia", "group": "A", "stage": "group"},
    {"date": "2026-06-19", "home": "South Africa", "away": "Paraguay", "group": "A", "stage": "group"},
    # Group B
    {"date": "2026-06-12", "home": "Canada", "away": "Bosnia and Herzegovina", "group": "B", "stage": "group"},
    {"date": "2026-06-12", "home": "Qatar", "away": "Croatia", "group": "B", "stage": "group"},
    {"date": "2026-06-16", "home": "Canada", "away": "Qatar", "group": "B", "stage": "group"},
    {"date": "2026-06-16", "home": "Croatia", "away": "Bosnia and Herzegovina", "group": "B", "stage": "group"},
    {"date": "2026-06-20", "home": "Canada", "away": "Croatia", "group": "B", "stage": "group"},
    {"date": "2026-06-20", "home": "Bosnia and Herzegovina", "away": "Qatar", "group": "B", "stage": "group"},
    # Group C
    {"date": "2026-06-12", "home": "USA", "away": "Turkey", "group": "C", "stage": "group"},
    {"date": "2026-06-12", "home": "Algeria", "away": "Sweden", "group": "C", "stage": "group"},
    {"date": "2026-06-16", "home": "USA", "away": "Algeria", "group": "C", "stage": "group"},
    {"date": "2026-06-16", "home": "Sweden", "away": "Turkey", "group": "C", "stage": "group"},
    {"date": "2026-06-20", "home": "USA", "away": "Sweden", "group": "C", "stage": "group"},
    {"date": "2026-06-20", "home": "Turkey", "away": "Algeria", "group": "C", "stage": "group"},
    # Group D
    {"date": "2026-06-13", "home": "Argentina", "away": "Morocco", "group": "D", "stage": "group"},
    {"date": "2026-06-13", "home": "Ivory Coast", "away": "Scotland", "group": "D", "stage": "group"},
    {"date": "2026-06-17", "home": "Argentina", "away": "Ivory Coast", "group": "D", "stage": "group"},
    {"date": "2026-06-17", "home": "Scotland", "away": "Morocco", "group": "D", "stage": "group"},
    {"date": "2026-06-21", "home": "Argentina", "away": "Scotland", "group": "D", "stage": "group"},
    {"date": "2026-06-21", "home": "Morocco", "away": "Ivory Coast", "group": "D", "stage": "group"},
    # Group E
    {"date": "2026-06-13", "home": "Brazil", "away": "Cape Verde", "group": "E", "stage": "group"},
    {"date": "2026-06-13", "home": "Saudi Arabia", "away": "Belgium", "group": "E", "stage": "group"},
    {"date": "2026-06-17", "home": "Brazil", "away": "Saudi Arabia", "group": "E", "stage": "group"},
    {"date": "2026-06-17", "home": "Belgium", "away": "Cape Verde", "group": "E", "stage": "group"},
    {"date": "2026-06-21", "home": "Brazil", "away": "Belgium", "group": "E", "stage": "group"},
    {"date": "2026-06-21", "home": "Cape Verde", "away": "Saudi Arabia", "group": "E", "stage": "group"},
    # Group F
    {"date": "2026-06-14", "home": "England", "away": "Iran", "group": "F", "stage": "group"},
    {"date": "2026-06-14", "home": "Senegal", "away": "Netherlands", "group": "F", "stage": "group"},
    {"date": "2026-06-18", "home": "England", "away": "Senegal", "group": "F", "stage": "group"},
    {"date": "2026-06-18", "home": "Netherlands", "away": "Iran", "group": "F", "stage": "group"},
    {"date": "2026-06-22", "home": "England", "away": "Netherlands", "group": "F", "stage": "group"},
    {"date": "2026-06-22", "home": "Iran", "away": "Senegal", "group": "F", "stage": "group"},
    # Group G
    {"date": "2026-06-14", "home": "France", "away": "Australia", "group": "G", "stage": "group"},
    {"date": "2026-06-14", "home": "Tunisia", "away": "Austria", "group": "G", "stage": "group"},
    {"date": "2026-06-18", "home": "France", "away": "Tunisia", "group": "G", "stage": "group"},
    {"date": "2026-06-18", "home": "Austria", "away": "Australia", "group": "G", "stage": "group"},
    {"date": "2026-06-22", "home": "France", "away": "Austria", "group": "G", "stage": "group"},
    {"date": "2026-06-22", "home": "Australia", "away": "Tunisia", "group": "G", "stage": "group"},
    # Group H
    {"date": "2026-06-15", "home": "Spain", "away": "Japan", "group": "H", "stage": "group"},
    {"date": "2026-06-15", "home": "Haiti", "away": "Switzerland", "group": "H", "stage": "group"},
    {"date": "2026-06-19", "home": "Spain", "away": "Haiti", "group": "H", "stage": "group"},
    {"date": "2026-06-19", "home": "Switzerland", "away": "Japan", "group": "H", "stage": "group"},
    {"date": "2026-06-23", "home": "Spain", "away": "Switzerland", "group": "H", "stage": "group"},
    {"date": "2026-06-23", "home": "Japan", "away": "Haiti", "group": "H", "stage": "group"},
    # Group I
    {"date": "2026-06-11", "home": "Germany", "away": "Ecuador", "group": "I", "stage": "group"},
    {"date": "2026-06-11", "home": "Jordan", "away": "Portugal", "group": "I", "stage": "group"},
    {"date": "2026-06-15", "home": "Germany", "away": "Jordan", "group": "I", "stage": "group"},
    {"date": "2026-06-15", "home": "Portugal", "away": "Ecuador", "group": "I", "stage": "group"},
    {"date": "2026-06-19", "home": "Germany", "away": "Portugal", "group": "I", "stage": "group"},
    {"date": "2026-06-19", "home": "Ecuador", "away": "Jordan", "group": "I", "stage": "group"},
    # Group J
    {"date": "2026-06-12", "home": "Uruguay", "away": "South Korea", "group": "J", "stage": "group"},
    {"date": "2026-06-12", "home": "Curacao", "away": "Panama", "group": "J", "stage": "group"},
    {"date": "2026-06-16", "home": "Uruguay", "away": "Curacao", "group": "J", "stage": "group"},
    {"date": "2026-06-16", "home": "Panama", "away": "South Korea", "group": "J", "stage": "group"},
    {"date": "2026-06-20", "home": "Uruguay", "away": "Panama", "group": "J", "stage": "group"},
    {"date": "2026-06-20", "home": "South Korea", "away": "Curacao", "group": "J", "stage": "group"},
    # Group K
    {"date": "2026-06-13", "home": "Colombia", "away": "Egypt", "group": "K", "stage": "group"},
    {"date": "2026-06-13", "home": "DR Congo", "away": "Norway", "group": "K", "stage": "group"},
    {"date": "2026-06-17", "home": "Colombia", "away": "DR Congo", "group": "K", "stage": "group"},
    {"date": "2026-06-17", "home": "Norway", "away": "Egypt", "group": "K", "stage": "group"},
    {"date": "2026-06-21", "home": "Colombia", "away": "Norway", "group": "K", "stage": "group"},
    {"date": "2026-06-21", "home": "Egypt", "away": "DR Congo", "group": "K", "stage": "group"},
    # Group L
    {"date": "2026-06-14", "home": "New Zealand", "away": "Ghana", "group": "L", "stage": "group"},
    {"date": "2026-06-14", "home": "Iraq", "away": "Uzbekistan", "group": "L", "stage": "group"},
    {"date": "2026-06-18", "home": "New Zealand", "away": "Iraq", "group": "L", "stage": "group"},
    {"date": "2026-06-18", "home": "Uzbekistan", "away": "Ghana", "group": "L", "stage": "group"},
    {"date": "2026-06-22", "home": "New Zealand", "away": "Uzbekistan", "group": "L", "stage": "group"},
    {"date": "2026-06-22", "home": "Ghana", "away": "Iraq", "group": "L", "stage": "group"},
    # Round of 32
    {"date": "2026-06-24", "home": "1A", "away": "3C/D/E", "stage": "round_of_32"},
    {"date": "2026-06-24", "home": "2A", "away": "2B", "stage": "round_of_32"},
    {"date": "2026-06-25", "home": "1B", "away": "3A/C/D", "stage": "round_of_32"},
    {"date": "2026-06-25", "home": "1C", "away": "3A/B/F", "stage": "round_of_32"},
    {"date": "2026-06-26", "home": "2C", "away": "2D", "stage": "round_of_32"},
    {"date": "2026-06-26", "home": "1D", "away": "3E/F/G", "stage": "round_of_32"},
    {"date": "2026-06-27", "home": "1E", "away": "3D/F/G", "stage": "round_of_32"},
    {"date": "2026-06-27", "home": "2E", "away": "2F", "stage": "round_of_32"},
    {"date": "2026-06-28", "home": "1F", "away": "3G/H/I", "stage": "round_of_32"},
    {"date": "2026-06-28", "home": "1G", "away": "3H/I/J", "stage": "round_of_32"},
    {"date": "2026-06-29", "home": "2G", "away": "2H", "stage": "round_of_32"},
    {"date": "2026-06-29", "home": "1H", "away": "3I/J/K", "stage": "round_of_32"},
    {"date": "2026-06-30", "home": "1I", "away": "3J/K/L", "stage": "round_of_32"},
    {"date": "2026-06-30", "home": "2I", "away": "2J", "stage": "round_of_32"},
    {"date": "2026-07-01", "home": "1J", "away": "3K/L/A", "stage": "round_of_32"},
    {"date": "2026-07-01", "home": "2K", "away": "2L", "stage": "round_of_32"},
    # Round of 16
    {"date": "2026-07-03", "home": "W73", "away": "W78", "stage": "round_of_16"},
    {"date": "2026-07-03", "home": "W74", "away": "W77", "stage": "round_of_16"},
    {"date": "2026-07-04", "home": "W75", "away": "W80", "stage": "round_of_16"},
    {"date": "2026-07-04", "home": "W76", "away": "W79", "stage": "round_of_16"},
    {"date": "2026-07-05", "home": "W81", "away": "W86", "stage": "round_of_16"},
    {"date": "2026-07-05", "home": "W82", "away": "W85", "stage": "round_of_16"},
    {"date": "2026-07-06", "home": "W83", "away": "W88", "stage": "round_of_16"},
    {"date": "2026-07-06", "home": "W84", "away": "W87", "stage": "round_of_16"},
    # Quarter-finals
    {"date": "2026-07-08", "home": "W89", "away": "W92", "stage": "quarter_final"},
    {"date": "2026-07-08", "home": "W90", "away": "W91", "stage": "quarter_final"},
    {"date": "2026-07-09", "home": "W93", "away": "W96", "stage": "quarter_final"},
    {"date": "2026-07-09", "home": "W94", "away": "W95", "stage": "quarter_final"},
    # Semi-finals
    {"date": "2026-07-12", "home": "W97", "away": "W98", "stage": "semi_final"},
    {"date": "2026-07-13", "home": "W99", "away": "W100", "stage": "semi_final"},
    # Third place
    {"date": "2026-07-17", "home": "L101", "away": "L102", "stage": "third_place"},
    # Final
    {"date": "2026-07-19", "home": "W101", "away": "W102", "stage": "final"},
]


TEAM_NAME_ALIASES = {
    "USA": "United States",
    "IR Iran": "Iran",
    "Korea Republic": "South Korea",
    "Côte d'Ivoire": "Ivory Coast",
    "DR Congo": "Congo DR",
    "Turkey": "Türkiye",
    "Bosnia and Herzegovina": "Bosnia-Herzegovina",
    "Cape Verde": "Cabo Verde",
    "Czechia": "Czech Republic",
    "Türkiye": "Turkey",
    "Ivory Coast": "Côte d'Ivoire",
}
