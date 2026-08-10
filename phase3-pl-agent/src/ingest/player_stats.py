import pandas as pd


def load_player_stats(csv_path="data/player_data/player.csv"):
    """
    Load player season statistics from CSV.

    Returns a list of dictionaries that can be ingested into ChromaDB.
    """

    df = pd.read_csv(csv_path)

    documents = []

    for _, row in df.iterrows():

        player = str(row["player_name"]).strip()
        team = str(row["team_title"]).strip()
        year = int(row["year"])

        games = int(row["games"]) if pd.notna(row["games"]) else 0
        minutes = int(row["time"]) if pd.notna(row["time"]) else 0
        goals = int(row["goals"]) if pd.notna(row["goals"]) else 0
        assists = int(row["assists"]) if pd.notna(row["assists"]) else 0
        yellow = int(row["yellow_cards"]) if pd.notna(row["yellow_cards"]) else 0
        red = int(row["red_cards"]) if pd.notna(row["red_cards"]) else 0
        text = (
            f"Player: {player}. "
            f"Club: {team}. "
            f"Season: {year}. "
            f"Games: {games}. "
            f"Minutes: {minutes}. "
            f"Goals: {goals}. "
            f"Assists: {assists}. "
            f"Yellow Cards: {yellow}. "
            f"Red Cards: {red}."
        )

        documents.append(
            {
                "player": player,
                "team": team,
                "year": year,
                "games": games,
                "minutes": minutes,
                "goals": goals,
                "assists": assists,
                "yellow_cards": yellow,
                "red_cards": red,
                "text": text,
            }
        )

    print(f"Loaded {len(documents)} player seasons.")

    return documents