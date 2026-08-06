import os
import re

# Matches lines like:
# 15:00  Arsenal FC 2-1 Chelsea FC
# Arsenal FC 2-1 Chelsea FC
MATCH_RE = re.compile(
    r"^\s*(?:\d{1,2}:\d{2}\s+)?"
    r"(.+?)\s+"
    r"(\d+)-(\d+)"
    r"(?:\s+\(\d+-\d+\))?"
    r"\s+(.+?)\s*$"
)


def load_matches(data_path="data/openfootball"):

    documents = []

    for season in sorted(os.listdir(data_path)):

        # Only folders like 2015-16
        if not re.fullmatch(r"20\d{2}-\d{2}", season):
            continue

        # Only 2015 onwards
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
            errors="ignore"
        ) as f:

            for raw in f:

                line = raw.strip()

                # -------------------------
                # Skip blank lines
                # -------------------------
                if not line:
                    continue

                # -------------------------
                # Skip comments/header
                # -------------------------
                if (
                    line.startswith("=")
                    or line.startswith("#")
                    or line.startswith("Pos")
                    or line.startswith("Team")
                    or line.startswith("P ")
                    or line.startswith("Pts")
                    or "Table" in line
                    or "Standings" in line
                    or "Attendance" in line
                    or "Referee" in line
                ):
                    continue

                # -------------------------
                # Matchday heading
                # -------------------------
                if "Matchday" in line:
                    current_matchday = line
                    continue

                # -------------------------
                # Skip weekday/date rows
                # -------------------------
                if line.startswith((
                    "Mon",
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat",
                    "Sun"
                )):
                    continue

                m = MATCH_RE.match(line)

                if not m:
                    continue

                home = m.group(1).strip()
                hg = int(m.group(2))
                ag = int(m.group(3))
                away = m.group(4).strip()

                # -------------------------
                # Skip malformed rows
                # -------------------------
                if re.match(r"^\d+\s", home):
                    continue

                if len(home) < 3 or len(away) < 3:
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

                documents.append(
                    {
                        "season": season,
                        "competition": "Premier League",
                        "matchday": current_matchday,
                        "home": home,
                        "away": away,
                        "home_goals": hg,
                        "away_goals": ag,
                        "winner": winner,
                        "text": text,
                    }
                )

    print(f"Loaded {len(documents)} Premier League matches.")

    return documents