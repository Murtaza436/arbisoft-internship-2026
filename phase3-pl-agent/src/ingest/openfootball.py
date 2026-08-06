import os
import re

TEAM_MAP = {
    "Arsenal": "Arsenal FC",
    "Chelsea": "Chelsea FC",
    "Liverpool": "Liverpool FC",
    "Manchester City": "Manchester City FC",
    "Manchester United": "Manchester United FC",
    "Leicester City": "Leicester City FC",
    "Newcastle United": "Newcastle United FC",
    "West Ham United": "West Ham United FC",
    "Aston Villa": "Aston Villa FC",
    "Everton": "Everton FC",
    "Fulham": "Fulham FC",
    "Brentford": "Brentford FC",
    "Burnley": "Burnley FC",
    "Crystal Palace": "Crystal Palace FC",
    "Ipswich Town": "Ipswich Town FC",
    "Leeds United": "Leeds United FC",
    "Nottingham Forest": "Nottingham Forest FC",
    "Southampton": "Southampton FC",
    "Sunderland": "Sunderland AFC",
    "Tottenham Hotspur": "Tottenham Hotspur FC",
    "Watford": "Watford FC",
    "West Bromwich Albion": "West Bromwich Albion FC",
    "Wolverhampton Wanderers": "Wolverhampton Wanderers FC",
    "Bournemouth": "AFC Bournemouth",
    "Brighton & Hove Albion": "Brighton & Hove Albion FC",
}

# Old format:
# Manchester United 2-1 Chelsea
OLD_RE = re.compile(
    r"^\s*(?:\d{1,2}:\d{2}\s+)?"
    r"(.+?)\s+"
    r"(\d+)-(\d+)"
    r"(?:\s+\(\d+-\d+\))?"
    r"\s+(.+?)\s*$"
)

# New format:
# Manchester United v Chelsea 2-1 (1-0)
NEW_RE = re.compile(
    r"^\s*(?:\d{1,2}:\d{2}\s+)?"
    r"(.+?)\s+v\s+"
    r"(.+?)\s+"
    r"(\d+)-(\d+)"
    r"(?:\s+\(\d+-\d+\))?\s*$"
)


def normalize(team):
    return TEAM_MAP.get(team.strip(), team.strip())


def load_matches(data_path="data/openfootball"):

    documents = []

    for season in sorted(os.listdir(data_path)):

        if not re.fullmatch(r"\d{4}-\d{2}", season):
            continue

        if int(season[:4]) < 2015:
            continue

        season_file = os.path.join(
            data_path,
            season,
            "1-premierleague.txt"
        )

        if not os.path.exists(season_file):
            continue

        current_matchday = ""

        with open(
            season_file,
            encoding="utf-8",
            errors="ignore",
        ) as f:

            for raw in f:

                line = raw.strip()

                if not line:
                    continue

                if line.startswith("="):
                    continue

                if line.startswith("#"):
                    continue

                if line.startswith(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")):
                    continue

                if "Matchday" in line:
                    current_matchday = line
                    continue

                lower = line.lower()

                if any(x in lower for x in [
                    "table",
                    "standings",
                    "attendance",
                    "statistics",
                    "top scorers",
                    "position",
                    "pts",
                    "played",
                    "wins",
                    "draws",
                    "losses",
                ]):
                    continue

                home = away = None

                old = OLD_RE.match(line)
                new = NEW_RE.match(line)

                if new:
                    home = normalize(new.group(1))
                    away = normalize(new.group(2))
                    hg = int(new.group(3))
                    ag = int(new.group(4))

                elif old:
                    home = normalize(old.group(1))
                    hg = int(old.group(2))
                    ag = int(old.group(3))
                    away = normalize(old.group(4))

                else:
                    continue

                if hg > ag:
                    winner = home
                elif ag > hg:
                    winner = away
                else:
                    winner = "Draw"

                text = (
                    f"Competition: Premier League. "
                    f"Season: {season}. "
                    f"Matchday: {current_matchday}. "
                    f"Home Team: {home}. "
                    f"Away Team: {away}. "
                    f"Score: {hg}-{ag}. "
                    f"Winner: {winner}."
                )

                documents.append({
                    "season": season,
                    "competition": "Premier League",
                    "matchday": current_matchday,
                    "home": home,
                    "away": away,
                    "home_goals": hg,
                    "away_goals": ag,
                    "winner": winner,
                    "text": text,
                })

    print(f"Loaded {len(documents)} Premier League matches.")
    return documents