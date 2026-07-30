TEST_QUESTIONS = [
    {
        'question': 'Who is currently top of the Premier League?',
        'expected_source': 'get_standings',
        'type': 'live',
    },
    {
        'question': 'Who is the top scorer in the Premier League this season?',
        'expected_source': 'get_top_scorers',
        'type': 'live',
    },
    {
        'question': 'What are the upcoming Premier League fixtures?',
        'expected_source': 'get_upcoming_fixtures',
        'type': 'live',
    },
    {
        'question': 'What were the recent Premier League results?',
        'expected_source': 'get_recent_results',
        'type': 'live',
    },
    {
        'question': 'How did Jamie Vardy perform in the 2015-16 season?',
        'expected_source': 'search_historical_stats',
        'type': 'historical',
    },
    {
        'question': 'How many goals did Mohamed Salah score in 2017-18?',
        'expected_source': 'search_historical_stats',
        'type': 'historical',
    },
    {
        'question': 'What were Manchester City stats in the 2018-19 season?',
        'expected_source': 'search_historical_stats',
        'type': 'historical',
    },
    {
        'question': 'Tell me about Arsenal latest transfer news',
        'expected_source': 'brave_search',
        'type': 'news',
    },
    {
        'question': 'What is the latest Premier League manager news?',
        'expected_source': 'brave_search',
        'type': 'news',
    },
    {
        'question': 'Show me Chelsea recent results',
        'expected_source': 'get_team_matches',
        'type': 'live',
    },
]


def run_evaluation(agent_fn, memory_fn):
    results = []
    for q in TEST_QUESTIONS:
        memory = memory_fn()
        answer = agent_fn(q['question'], memory)
        results.append({
            'question': q['question'],
            'expected_source': q['expected_source'],
            'type': q['type'],
            'answer_preview': answer[:200],
            'answered': len(answer) > 50,
        })
    return results
