import json
import uuid
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text as sql_text

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


@match.get("/links/all", tags=['matchs'])
async def get_all_links(page: int = Query(1, gt=0), per_page: int = Query(60, gt=0)):
    try:
        skip = (page - 1) * per_page
        limit = per_page
        matchs = matchs_links_collection.find().skip(skip).limit(limit)
        matchs_data = [
            link for link in matchs
        ]
        for link in matchs_data:
            link["_id"] = str(link["_id"])
        return JSONResponse(content=matchsLinksEntity(matchs_data), status_code=200)
    except:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron enlaces que cumplan con los criterios.",
        )

@match.get("/all", tags=['matchs'])
async def get_all_matchs(page: int = Query(1, gt=0), per_page: int = Query(60, gt=0)):
    try:
        skip = (page - 1) * per_page
        limit = per_page
        matchs = matchs_data_collection.find().skip(skip).limit(limit)
        matchs_data = [
            item for item in matchs
        ]
        for link in matchs_data:
            link["_id"] = str(link["_id"])
        return JSONResponse(content=matchsEntity(matchs_data), status_code=200)
    except:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron enlaces que cumplan con los criterios.",
        )

@match.get("/links", tags=['matchs'])
async def get_links(yearr: str, cod: str):
    try:
        yearr_list = [int(year) for year in yearr.split(", ")]
        cod_list = cod.split(", ")
        filters = {"year": {"$in": yearr_list}, "code": {"$in": cod_list}}
        matchs = matchs_links_collection.find(filters)
        matchs_data = [link for link in matchs]
        for link in matchs_data:
            link["_id"] = str(link["_id"])
        return JSONResponse(content=matchsLinksEntity(matchs_data), status_code=200)
    except:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron enlaces que cumplan con los criterios.",
        )

@match.get("/", tags=['matchs'])
async def get_matchs(yearr: str, cod: str):
    try:
        yearr_list = [int(year) for year in yearr.split(", ")]
        cod_list = cod.split(", ")
        filters = {"year": {"$in": yearr_list}, "code": {"$in": cod_list}}
        matchs = matchs_data_collection.find(filters)
        matchs_data = [item for item in matchs]
        for link in matchs_data:
            link["_id"] = str(link["_id"])
        return JSONResponse(content=matchsEntity(matchs_data), status_code=200)
    except:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron enlaces que cumplan con los criterios.",
        )

@match.post("/links", tags=['matchs'])
async def save_links(yearr: str, cod: str):
    query = ""
    yearr_list = [int(year) for year in yearr.split(", ")]
    cod_list = cod.split(", ")
    if (
        len(cod_list) == 1 and len(yearr_list) == 1
    ):  # Si cod_list tiene un solo elemento
        query = f"SELECT * FROM torneos_primera_arg.url_equipos WHERE year = '{yearr_list[0]}' AND code = '{cod_list[0]}'"
    elif len(yearr_list) == 1 and len(cod_list) > 1:
        query = f"SELECT * FROM torneos_primera_arg.url_equipos WHERE year = '{yearr_list[0]}' AND code IN {tuple(cod_list)}"
    elif len(yearr_list) > 1 and len(cod_list) == 1:
        query = f"SELECT * FROM torneos_primera_arg.url_equipos WHERE year IN {tuple(yearr_list)} AND code = '{cod_list[0]}'"
    else:
        query = f"SELECT * FROM torneos_primera_arg.url_equipos WHERE year IN {tuple(yearr_list)} AND code IN {tuple(cod_list)}"
    try:
        filters = {"year": {"$in": yearr_list}, "code": {"$in": cod_list}}
        existing_records = matchs_links_collection.find(filters)
        cur = sql_conn.cursor()
        cur.execute(query)
        teams_urls = cur.fetchall()
        teams_url_dict = []
        for team in teams_urls:
            team_dict = {
                "code": team[0],
                "name": team[1],
                "url": team[2],
                "country": team[3],
                "year": team[4],
            }
            teams_url_dict.append(team_dict)
        for item in teams_url_dict:
            matchs_links = get_matchs_links(item["url"])
            item["matchs_urls"] = matchs_links
        for item in teams_url_dict:
            match_links = MatchLinks(
                id=str(uuid.uuid4()),
                code=item["code"],
                name=item["name"],
                url=item["url"],
                country=item["country"],
                year=item["year"],
                matchs_urls=item["matchs_urls"],
            )
            matchs_links_collection.insert_one(match_links.dict())
        return JSONResponse(
            content={"message": "match link saved success"}, status_code=201
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Cannot find the request data: {str(e)}"
        )


@match.post("/data", tags=['matchs'])
async def post_matchs(yearr: str, cod: str):
    try:
        matchs_data_list = []
        yearr_list = [int(year) for year in yearr.split(", ")]
        cod_list = cod.split(", ")
        filters = {"year": {"$in": yearr_list}, "code": {"$in": cod_list}}
        matchs = matchs_links_collection.find(filters)
        matchs_links = [link for link in matchs]
        for item in matchs_links:
            for url in item["matchs_urls"]:
                print(url)
                match_data = get_match_data(
                    item["code"], item["name"], item["country"], item["year"], url
                )
                matchs_data_list.append(match_data)
        print(
            "---------------------------MATCH DATA----------------------------"
        )
        print(matchs_data_list)
        match_ = matchs_data_collection.find_one({"link": url})
        if match_ is None:
            for item in matchs_data_list:
                match_data_ = MatchData(
                    id=str(uuid.uuid4()),
                    code=item["code"],
                    name=item["name"],
                    country=item["country"],
                    year=item["year"],
                    date=item["date"],
                    status=item["status"],
                    home_team=item["home_team"],
                    away_team=item["away_team"],
                    link=item["link"],
                    score=item["score"],
                    tournament=item["tournament"],
                    local_scorers=item["local_scorers"],
                    away_scorers=item["away_scorers"],
                    local_yellow_cards=item["local_yellow_cards"],
                    away_yellow_cards=item["away_yellow_cards"],
                    statistics=item["statistics"]
                )
                matchs_data_collection.insert_one(match_data_.dict())
            return JSONResponse(
                content={"message": "New match was created successfully"},
                status_code=201,
            )
        else:
            return JSONResponse(
                content={"message": "Match is already created"}, status_code=400
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")