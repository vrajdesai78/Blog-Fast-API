from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

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

@app.get("/")
def root():
    return {"message":"Hello World"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    cursor.execute("""select * from posts""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
        (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data":new_post}

@app.get("/posts/{id}")
def get_posts_by_id(id: int):
    cursor.execute("""select * from posts where id = %s""", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int):
    cursor.execute("""delete from posts where id = %s returning *""", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} not found")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_posts(id: int, updated_post: Post):
    cursor.execute("""update posts set title=%s, content=%s, published=%s where id=%s returning *""", 
        (updated_post.title, updated_post.content, updated_post.published, id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} not found")
    conn.commit()
    return {"data": post}
