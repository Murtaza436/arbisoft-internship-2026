from src.ingest.pipeline import get_collection


def parse_stat_line(line: str) -> dict:
    """Parse a stat line into a dictionary."""
    try:
        parts = {}
        for segment in line.split('|'):
            segment = segment.strip()
            if ':' in segment:
                key, value = segment.split(':', 1)
                parts[key.strip()] = value.strip()
        return parts
    except Exception:
        return {}


def search_historical_stats(query: str, n_results: int = 20) -> str:
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        chunks = results['documents'][0]
        if not chunks:
            return 'No historical records found for this query.'

        player_totals = {}

        for chunk in chunks:
            parts = parse_stat_line(chunk)
            if not parts:
                continue

            first_part = chunk.split('|')[0].strip()
            player_name = first_part

            if player_name not in player_totals:
                player_totals[player_name] = {
                    'player': player_name,
                    'team': parts.get('Goals', ''),
                    'matches': 0,
                    'goals': 0,
                    'assists': 0,
                    'shots': 0,
                    'shots_on_target': 0,
                    'passes': 0,
                    'seasons': set(),
                }

            try:
                player_totals[player_name]['goals'] += int(
                    parts.get('Goals', '0').split()[0]
                )
            except Exception:
                pass
            try:
                player_totals[player_name]['assists'] += int(
                    parts.get('Assists', '0').split()[0]
                )
            except Exception:
                pass
            try:
                player_totals[player_name]['shots'] += int(
                    parts.get('Shots', '0').split()[0]
                )
            except Exception:
                pass
            try:
                player_totals[player_name]['shots_on_target'] += int(
                    parts.get('Shots on Target', '0').split()[0]
                )
            except Exception:
                pass
            try:
                player_totals[player_name]['passes'] += int(
                    parts.get('Passes Completed', '0').split()[0]
                )
            except Exception:
                pass

            season = parts.get('Season', '')
            if season:
                player_totals[player_name]['seasons'].add(season)
            player_totals[player_name]['matches'] += 1

        if not player_totals:
            return f'No aggregated stats found for: {query}'

        output = [f'Premier League Historical Stats - {query}\n']
        output.append(f'Based on {len(chunks)} match records from StatsBomb data\n')

        for player_name, stats in player_totals.items():
            seasons_str = ', '.join(sorted(stats['seasons'])) or 'Multiple seasons'
            output.append(f"Player: {player_name}")
            output.append(f"Seasons covered: {seasons_str}")
            output.append(f"Matches found: {stats['matches']}")
            output.append(f"Total Goals: {stats['goals']}")
            output.append(f"Total Assists: {stats['assists']}")
            output.append(f"Total Shots: {stats['shots']}")
            output.append(f"Total Shots on Target: {stats['shots_on_target']}")
            output.append(f"Total Passes Completed: {stats['passes']}")
            output.append("")

        output.append(
            "Note: Stats are aggregated from available StatsBomb match records "
            "(2015-16 to 2022-23). May not include all matches."
        )
        return '\n'.join(output)

    except Exception as e:
        return (
            f'RAG search failed: {str(e)}. '
            'Make sure you have run the ingestion pipeline first.'
        )
