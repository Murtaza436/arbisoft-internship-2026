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


def search_historical_stats(query: str, n_results: int = 50) -> str:
    try:
        collection = get_collection()
    except Exception as e:
        return (
            'Historical stats database not available. '
            'ChromaDB has not been ingested yet. '
            'Run the ingestion cell first in the Week 7 notebook.'
        )

    import re

    # Normalize search query
    query = query.lower()

    # Remove season references such as 2015-16 or 2023/24
    query = re.sub(r'\b\d{4}[-/]\d{2,4}\b', '', query)

    # Remove filler words
    for word in [
        'season',
        'premier',
        'league',
        'stats',
        'statistics',
        'show',
        'tell',
        'about',
    ]:
        query = query.replace(word, ' ')

    query = ' '.join(query.split())

    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, 20),
        )
        
        # FIX: Prevent IndexError if ChromaDB returns empty results
        if not results or not results.get('documents') or not results['documents']:
            return f'No historical records found for: {query}'

        chunks = results['documents'][0]
        metadatas = results['metadatas'][0] if results.get('metadatas') else []

        if not chunks:
            return f'No historical records found for: {query}'

        search_terms = query.lower().split()
        filtered_chunks = []
        for chunk in chunks:
            chunk_lower = chunk.lower()
            matched = sum(
                1 for term in search_terms
                if len(term) > 3 and term in chunk_lower
            )
            if matched >= 1:
                filtered_chunks.append(chunk)

        if not filtered_chunks:
            filtered_chunks = chunks[:5]

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

        player_totals = dict(
            sorted(
                player_totals.items(),
                key=lambda x: (
                    x[1]["goals"],
                    x[1]["assists"],
                    x[1]["matches"],
                ),
                reverse=True,
            )
        )

        sorted_players = sorted(
            player_totals.items(),
            key=lambda x: x[1]['goals'] + x[1]['assists'],
            reverse=True,
        )

        output = [f'## Premier League Historical Stats\n**Query:** {query}\n']
        output.append(
            f'*Based on {len(filtered_chunks)} match records from StatsBomb data*\n'
        )

        for player_name, stats in sorted_players[:1]:
            seasons_str = (
                ', '.join(sorted(stats['seasons']))
                if stats['seasons'] else 'Multiple seasons'
            )
            output.append(f'**Player:** {player_name}')
            output.append(f'**Seasons:** {seasons_str}')
            output.append(f'**Matches Found:** {stats["matches"]}\n')
            output.append('| Stat | Value |')
            output.append('|------|-------|')
            output.append(f'| Goals | {stats["goals"]} |')
            output.append(f'| Assists | {stats["assists"]} |')
            output.append(f'| Shots | {stats["shots"]} |')
            output.append(f'| Shots on Target | {stats["shots_on_target"]} |')
            output.append(f'| Passes Completed | {stats["passes"]} |')
            if stats['goals'] > 0 and stats['shots'] > 0:
                conv = (stats['goals'] / stats['shots']) * 100
                output.append(f'| Shot Conversion Rate | {conv:.1f}% |')
            output.append('')

        output.append(
            '*Stats from StatsBomb open data (2015-16 to 2022-23). '
            'Full coverage after Week 7 ingestion.*'
        )
        return '\n'.join(output)

    except Exception as e:
        return f'RAG search error: {str(e)}'
