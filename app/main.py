from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/poopoo")
async def toilet():
    return {"action_needed": "FLUSH!! for gods sake flush!!"}
