def matchLinkEntity(item) -> dict:
    return {
        "id": item["_id"],
        "code": item["code"],
        "name": item["name"],
        "url": item["url"],
        "country": item["country"],
        "year": item["year"],
        "matchs_urls": item["matchs_urls"]
    }

def matchsLinksEntity(entity) -> list:
    return [matchLinkEntity(item) for item in entity]