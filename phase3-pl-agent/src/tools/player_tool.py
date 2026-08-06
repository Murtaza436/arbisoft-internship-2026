import re
from src.ingest.pipeline import get_player_collection


def search_player_stats(query: str, n_results:200):

    try:
        collection = get_player_collection()
    except Exception:
        return "Player database not found. Run ingest_player_stats()."

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    docs = results["documents"][0]

    if not docs:
        return "No player found."

    player = None

    totals = {
        "games":0,
        "minutes":0,
        "goals":0,
        "assists":0,
        "yellow":0,
        "red":0,
    }

    seasons = []

    for doc in docs:

        if player is None:
            m = re.search(r"Player:\s*(.*)", doc)
            if m:
                player = m.group(1)

        season={}

        def grab(field):

            m=re.search(field+r":\s*([^\n]+)",doc)

            if m:
                return m.group(1).strip()

            return ""

        year=grab("Season")

        games=int(float(grab("Games") or 0))
        mins=int(float(grab("Minutes") or 0))
        goals=int(float(grab("Goals") or 0))
        assists=int(float(grab("Assists") or 0))
        yellow=int(float(grab("Yellow Cards") or 0))
        red=int(float(grab("Red Cards") or 0))

        totals["games"]+=games
        totals["minutes"]+=mins
        totals["goals"]+=goals
        totals["assists"]+=assists
        totals["yellow"]+=yellow
        totals["red"]+=red

        seasons.append({
            "year":year,
            "games":games,
            "goals":goals,
            "assists":assists
        })

    seasons.sort(key=lambda x:x["year"])

    out=[]

    out.append(f"# {player}\n")

    out.append("## Career Totals\n")

    out.append(f"Games: {totals['games']}")
    out.append(f"Minutes: {totals['minutes']}")
    out.append(f"Goals: {totals['goals']}")
    out.append(f"Assists: {totals['assists']}")
    out.append(f"Yellow Cards: {totals['yellow']}")
    out.append(f"Red Cards: {totals['red']}\n")

    out.append("## Season Breakdown\n")

    for s in seasons:

        out.append(
            f"{s['year']} — "
            f"{s['games']} games | "
            f"{s['goals']} goals | "
            f"{s['assists']} assists"
        )

    return "\n".join(out)