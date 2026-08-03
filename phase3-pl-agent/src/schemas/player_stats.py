from pydantic import BaseModel, field_validator


class PlayerMatchStats(BaseModel):
    player_name: str
    team: str
    opponent: str
    match_date: str
    season: str
    goals: int
    assists: int
    shots: int
    shots_on_target: int
    passes_completed: int
    minutes_played: int

    @field_validator('goals', 'assists', 'shots', 'shots_on_target', 'passes_completed', 'minutes_played')
    @classmethod
    def must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Stats cannot be negative')
        return v

    @field_validator('minutes_played')
    @classmethod
    def valid_minutes(cls, v):
        if v > 130:
            raise ValueError('Minutes played cannot exceed 130')
        return v
