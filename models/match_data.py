from typing import Dict, Optional
from pydantic import BaseModel

class MatchData(BaseModel):
    id: Optional[str]
    code: str
    name: str
    country: str
    year: int
    date: str
    status: str
    home_team: str
    away_team: str
    link: str
    score: str
    tournament: str
    local_scorers: str
    away_scorers: str
    local_yellow_cards: str
    away_yellow_cards: str
    statistics: Optional[dict]