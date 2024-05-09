def matchEntity(item) -> dict:
    return {
        "id": item.get("_id", ""),
        "code": item.get("code", ""),
        "name": item.get("name", ""),
        "country": item.get("country", ""),
        "year": item.get("year", ""),
        "date": item.get("date", ""),
        "status": item.get("status", ""),
        "home_team": item.get("home_team", ""),
        "away_team": item.get("away_team", ""),
        "link": item.get("link", ""),
        "score": item.get("score", ""),
        "tournament": item.get("tournament", ""),
        "local_scorers": item.get("local_scorers", ""),
        "away_scorers": item.get("away_scorers", ""),
        "local_yellow_cards": item.get("local_yellow_cards", ""),
        "away_yellow_cards": item.get("away_yellow_cards", ""),
        "statistics": item.get("statistics", {})
    }
    
def matchsEntity(entity) -> list:
    return [matchEntity(item) for item in entity]