from pydantic import BaseModel

class Team(BaseModel):
    name: str
    abbreviation: str
    color: str
    statcast_id: int
    statcast_code: str

class Game(BaseModel):
    home_team: Team
    away_team: Team