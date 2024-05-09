from typing import Dict, Optional
from pydantic import BaseModel

class MatchLinks(BaseModel):
    id: Optional[str]
    code: str
    name: str
    url: str
    country: str
    year: int
    matchs_urls: list