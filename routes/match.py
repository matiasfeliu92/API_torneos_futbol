import json
import uuid
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from helpers.utils import get_match_data, get_matchs_links
from models.match_data import MatchData
from models.match_links import MatchLinks
from config.mongo_db import mongo_conn
from config.sql_db import create_sql_connection
from schemas.match import matchEntity, matchsEntity
from schemas.matchs_links import matchsLinksEntity

sql_conn = create_sql_connection()
match = APIRouter(prefix="/matchs")
matchs_links_collection = mongo_conn["matchs_links"]
matchs_data_collection = mongo_conn["matchs_data"]

@match.get("/links/all", tags=["matchs"])
async def get_all_links(page: int = Query(1, gt=0), per_page: int = Query(60, gt=0)):
    try:
        skip = (page - 1) * per_page
        limit = per_page
        matchs = matchs_links_collection.find().skip(skip).limit(limit)
        matchs_data = [link for link in matchs]
        if len(matchs_data) == 0:
            return JSONResponse(
                status_code=404, content={"Detail": "Cannot find the request data"}
            )
        for link in matchs_data:
            link["_id"] = str(link["_id"])
        return JSONResponse(content=matchsLinksEntity(matchs_data), status_code=200)
    except Exception as e:
        return JSONResponse(status_code=500, content={"Detail": f"Error: {str(e)}"})

@match.get("/all", tags=["matchs"])
async def get_all_matchs(page: int = Query(1, gt=0), per_page: int = Query(60, gt=0)):
    try:
        skip = (page - 1) * per_page
        limit = per_page
        matchs = matchs_data_collection.find().skip(skip).limit(limit)
        matchs_data = [item for item in matchs]
        if len(matchs_data) == 0:
            return JSONResponse(
                status_code=404, content={"Detail": "Cannot find the request data"}
            )
        for link in matchs_data:
            link["_id"] = str(link["_id"])
        return JSONResponse(content=matchsEntity(matchs_data), status_code=200)
    except Exception as e:
        return JSONResponse(status_code=500, content={"Detail": f"Error: {str(e)}"})

@match.get("/links", tags=["matchs"])
async def get_links(yearr: str, cod: str):
    try:
        yearr_list = [int(year) for year in yearr.split(", ")]
        cod_list = cod.split(", ")
        filters = {"year": {"$in": yearr_list}, "code": {"$in": cod_list}}
        matchs = matchs_links_collection.find(filters)
        matchs_data = [link for link in matchs]
        if len(matchs_data) == 0:
            return JSONResponse(
                status_code=404, content={"Detail": "Cannot find the request data"}
            )
        for link in matchs_data:
            link["_id"] = str(link["_id"])
        return JSONResponse(content=matchsLinksEntity(matchs_data), status_code=200)
    except Exception as e:
        return JSONResponse(status_code=500, content={"Detail": f"Error: {str(e)}"})

@match.get("/", tags=["matchs"])
async def get_matchs(yearr: str, cod: str):
    try:
        yearr_list = [int(year) for year in yearr.split(", ")]
        cod_list = cod.split(", ")
        filters = {"year": {"$in": yearr_list}, "code": {"$in": cod_list}}
        matchs = matchs_data_collection.find(filters)
        matchs_data = [item for item in matchs]
        if len(matchs_data) == 0:
            return JSONResponse(
                status_code=404, content={"Detail": "Cannot find the request data"}
            )
        for link in matchs_data:
            link["_id"] = str(link["_id"])
        return JSONResponse(content=matchsEntity(matchs_data), status_code=200)
    except Exception as e:
        return JSONResponse(status_code=500, content={"Detail": f"Error: {str(e)}"})

@match.post("/links", tags=["matchs"])
async def save_links(yearr: int, cod: str, url: str, nombre: str = "", pais: str = ""):
    try:
        if yearr == "" or cod == "" or url == "" or nombre == "" or pais == "":
            return JSONResponse(
                status_code=400,
                content={"detail": "Bad request: Invalid or missing parameter"},
            )
        filters = {"year": yearr, "code": cod, "url": url}
        existing_record = matchs_links_collection.find_one(filter=filters)
        print("existing_record")
        print(existing_record is not None)
        if existing_record is not None:
            return JSONResponse(
                status_code=409,
                content={"detail": "That year and code is already saved"},
            )
        else:
            print("-----------EXISTING RECORD VACIO-------------")
            matchs_links = get_matchs_links(url)
            new_match_links = MatchLinks(
                id=str(uuid.uuid4()),
                code=cod,
                name=nombre,
                url=url,
                country=pais,
                year=yearr,
                matchs_urls=matchs_links,
            )
            matchs_links_collection.insert_one(new_match_links.dict())
            return {"message": "match link saved successfully"}
    except:
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

@match.post("/data", tags=["matchs"])
async def post_matchs(
    yearr: int, cod: str, index: int, url: str = "", nombre: str = "", pais: str = ""
):
    print(yearr)
    print(cod)
    matchs_data_list = []
    try:
        filters = {"year": yearr, "code": cod}
        matchs_links = matchs_links_collection.find_one(filters)
        if not matchs_links:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Bad request: Cannot find data for that year and code"
                },
            )
        print(matchs_links["matchs_urls"][index])
        match_ = matchs_data_collection.find_one(
            {"link": matchs_links["matchs_urls"][index]}
        )
        if match_:
            return JSONResponse(
                status_code=409, content={"detail": "The match found is already saved"}
            )
        match_data = get_match_data(
            matchs_links["code"],
            matchs_links["name"],
            matchs_links["country"],
            matchs_links["year"],
            matchs_links["matchs_urls"][index],
        )
        print(match_data)
        match_data_ = MatchData(
            id=str(uuid.uuid4()),
            code=match_data["code"],
            name=match_data["name"],
            country=match_data["country"],
            year=match_data["year"],
            date=match_data["date"],
            status=match_data["status"],
            home_team=match_data["home_team"],
            away_team=match_data["away_team"],
            link=match_data["link"],
            score=match_data["score"],
            tournament=match_data["tournament"],
            local_scorers=match_data["local_scorers"],
            away_scorers=match_data["away_scorers"],
            local_yellow_cards=match_data["local_yellow_cards"],
            away_yellow_cards=match_data["away_yellow_cards"],
            statistics=match_data["statistics"],
        )
        matchs_data_collection.insert_one(match_data_.dict())
        return JSONResponse(
            content={"message": "New match was created successfully"},
            status_code=201,
        )
    except:
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )