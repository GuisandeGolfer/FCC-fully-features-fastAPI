import psycopg2
from typing import List
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Response, status, HTTPException, Depends
from . import models, schemas  # to reference the 'Post' class,use schemas.Post
from .database import engine, get_db
from sqlalchemy.orm import Session
import time


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

'''
    The class below is a pydantic model which is inherently different from
    the posts database that is found in 'models.py'.

    The pydantic model defines what kind of response/request is sent from
    the browser and responded from the API.

    This is also called a schema model. this helps give restrictions to
    the user submitting data.
'''


while True:
    try:
        conn = psycopg2.connect(
            dbname='fastAPI',
            host='localhost', user='postgres', password='Diegito23!',
            port='5432',
            cursor_factory=RealDictCursor)
        cursor = conn.cursor()

        print("data: connection to Database was successful")
        break
    except Exception as error:
        print("connection to database failed")
        print("Error: ", error)
        time.sleep(4)
'''
CRUD API outline of routes:

app.get(/) ---- R-ead
app.get(/posts) --- R-ead
app.get(/posts/{id}) --- R-ead
app.post(/posts) --- C-reate
app.delete(/posts/{id}) --- D-elete
app.put(/posts/{id}) --- U-pdate

C - reate
R - ead
U - pdate
D - elete

localhost:8000/docs -> to see this in the browser.

'''


@app.get('/')
def read_root():
    return {"message": "Welcome to my API"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db), response_model=List[schemas.Post]):

    posts = db.query(models.Post).all()

    return posts


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db), response_model=schemas.Post):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()
    # print(post)
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} was not found')

    return post


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(
    # """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s)
    # RETURNING * """,
    #       (post.title, post.content, post.published)) # order matters
    # new_post = cursor.fetchone()
    #
    # conn.commit()
    new_post = models.Post(**post.dict())  # unpack dict inside 'models.Post()'

    # how to add to postgreSQL database.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """ DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone()
    #
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id == id)

    if deleted_post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} does not exist')

    deleted_post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/posts/{id}')
def update_post(id: int,
                updated_post:
                schemas.PostCreate,
                db: Session = Depends(get_db),
                response_model=schemas.Post):
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} does not exist')

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()

    '''
        I got stumped with def update_post

        i kept trying to do post.dict() on line 142 and
        it was hitting the post var
        on line 136. when I wanted to instead update the query with
        the actual updated post that is in the body of the API route
        reponse. which is now named 'updated_post' on line 130.
    '''


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    new_user = models.User(**user.dict())  # unpack dict inside 'models.Post()'

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
