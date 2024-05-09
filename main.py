from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text as sql_text
import pandas as pd
import sys
import os
import json

from config.sql_db import create_sql_connection
# from helpers.utils import get_team_data
sys.path.append('C:\\Users\\PC\\Documents\\Matias\\torneos_primera_division_arg')
from routes.match import match

app = FastAPI()
app.include_router(match)

conn = create_sql_connection()

@app.get("/index")
def read_root():
    return {"Hello": "World"}