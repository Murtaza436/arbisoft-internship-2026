from pydantic import BaseModel
from typing import List


class TeamStanding(BaseModel):
    position: int
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class CurrentStandings(BaseModel):
    season: str
    matchday: int
    top_team: str
    top_scorer: str
    standings: List[TeamStanding]
    teams_in_top_4: List[str]
    teams_in_relegation: List[str]
