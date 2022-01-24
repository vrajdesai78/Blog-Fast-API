from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from typing import List
from .routers import post, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', 
            user='postgres', password='vdesai', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull")
        break

    except Exception as error:
        print(f"Error occured: {error}")
        time.sleep(3)

my_posts = [{"title": "title of post1", "content":"content of post 1", "id":1},
     {"title":"favourite foods", "content": "I like pizza", "id":2}]

def find_post(id):
    for post in my_posts:
        if(post['id'] == id):
            return post
    return None

app.include_router(post.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message":"Hello World"}
