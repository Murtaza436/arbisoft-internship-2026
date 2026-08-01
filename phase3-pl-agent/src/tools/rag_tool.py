from src.ingest.pipeline import get_collection


def parse_stat_line(line: str) -> dict:
    try:
        parts = {}
        segments = line.split('|')
        if segments:
            parts['player_name'] = segments[0].strip()
        for segment in segments[1:]:
            segment = segment.strip()
            if ':' in segment:
                key, value = segment.split(':', 1)
                parts[key.strip()] = value.strip()
        return parts
    except Exception:
        return {}


def extract_player_name_from_query(query: str) -> str:
    stop_words = [
        'goals', 'assists', 'shots', 'passes', 'stats', 'performance',
        'premier', 'league', 'season', 'total', 'how', 'many', 'did',
        'score', 'in', 'the', 'for', 'at', 'his', 'her', 'their',
        '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022',
        'leicester', 'liverpool', 'tottenham', 'manchester', 'arsenal',
        'chelsea', 'city', 'united', 'spurs',
    ]
    words = query.lower().split()
    name_words = [w for w in words if w not in stop_words and len(w) > 2]
    return ' '.join(name_words[:3]) if name_words else ''


def search_historical_stats(query: str, n_results: int = 50) -> str:
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        chunks = results['documents'][0]
        metadatas = results['metadatas'][0] if results.get('metadatas') else []

        if not chunks:
            return 'No historical records found for this query.'

        search_terms = query.lower().split()

        filtered_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            matched = sum(
                1 for term in search_terms
                if len(term) > 3 and term in chunk_lower
            )
            if matched >= 2:
                filtered_chunks.append(chunk)

        if not filtered_chunks:
            filtered_chunks = chunks[:10]

        player_totals = {}

        for chunk in filtered_chunks:
            parts = parse_stat_line(chunk)
            if not parts:
                continue

            player_name = parts.get('player_name', 'Unknown')
            if not player_name or player_name == 'Unknown':
                continue

            if player_name not in player_totals:
                player_totals[player_name] = {
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
            return f'No stats found for: {query}'

        sorted_players = sorted(
            player_totals.items(),
            key=lambda x: x[1]['goals'] + x[1]['assists'],
            reverse=True,
        )

        output = [f'Premier League Historical Stats - {query}\n']
        output.append(
            f'Based on {len(filtered_chunks)} relevant match records '
            f'from StatsBomb data\n'
        )

        for player_name, stats in sorted_players[:1]:
            seasons_str = (
                ', '.join(sorted(stats['seasons']))
                if stats['seasons'] else 'Season data unavailable'
            )
            output.append(f"Player: {player_name}")
            output.append(f"Seasons in data: {seasons_str}")
            output.append(f"Matches found: {stats['matches']}")
            output.append(f"Total Goals: {stats['goals']}")
            output.append(f"Total Assists: {stats['assists']}")
            output.append(f"Total Shots: {stats['shots']}")
            output.append(f"Total Shots on Target: {stats['shots_on_target']}")
            output.append(f"Total Passes Completed: {stats['passes']}")
            if stats['goals'] > 0 and stats['shots'] > 0:
                conversion = (stats['goals'] / stats['shots']) * 100
                output.append(f"Shot Conversion Rate: {conversion:.1f}%")
            output.append("")

        output.append(
            "Note: Stats aggregated from StatsBomb match records. "
            "Week 5 has 1 season ingested. Full 8 seasons ingested in Week 7."
        )
        return '\n'.join(output)

    except Exception as e:
        return (
            f'RAG search failed: {str(e)}. '
            'Make sure ingestion pipeline has been run first.'
        )

