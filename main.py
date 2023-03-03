from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

from typing import Optional, Union

app = FastAPI()

class Post(BaseModel): 
    title: str 
    content: str 
    published: bool = True # optional schema
    rating: Optional[int] = None


my_posts = [
    {"title": "title of post 1","content": "content of post 1", "id": 2}, 
    {"title": "favorite foods","content": "spaghetti, pizza, hot dogs", "id": 1}
]

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

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get('/') 
def read_root(): 
    return {"message": "Welcome to my API"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts} 


@app.get("/posts/{id}")
def get_post(id: int, response: Response): # validate that param is an int, response: <Response> object from FastAPI

    post = find_post(id) # we needed to convert the 'id' into an int because we get the id as a string from the client-side (postman)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} was not found')

    return {"This is your requested post": post} 


@app.post("/posts", status_code=status.HTTP_201_CREATED) #HTTP best practices.
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0,10000)
    my_posts.append(post_dict)
    return {"Data": post_dict}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} does not exist')

    my_posts.pop(index)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id: int, post: Post):

    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} does not exist')

    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict

    return {'data': my_posts}
    