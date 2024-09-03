from app.schemas import DownloadRequest, TaskResponse, TaskStatus, TaskResult
from fastapi import FastAPI, BackgroundTasks, HTTPException
# import aiohttp
# import asyncio
import uuid
import requests
from typing import Dict


app = FastAPI()

# TODO: add sqllite database, or maybe Google FireStore
tasks: Dict[str, Dict] = {}


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#

async def start_prompt_process(task_id: str, url: str, detail: str):
    tasks[task_id]["status"] = TaskStatus.IN_PROGRESS
    try:
        success = requests.get("http://google.com")
        # async with aiohttp.ClientSession() as session:
        if success.text:
            # TODO: run youtube download script with parameters
            tasks[task_id]["transcription"] = success.json()
            tasks[task_id]["status"] = TaskStatus.COMPLETED

    except Exception as e:
        tasks[task_id]["status"] = TaskStatus.FAILED
        tasks[task_id]["error"] = str(e)


@app.post("/start-download", response_model=TaskResponse)
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": TaskStatus.PENDING}
    background_tasks.add_task(start_prompt_process, task_id, request.url, request.detail_level)
    return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)


# @app.get("/task-result/{task_id}", response_model=TaskResponse)
# async def get_task_result(task_id: str):
#     if task_id not in tasks:
#         raise HTTPException(status_code=404, detail="Task Not Found")
#
#     task = tasks[task_id]
#     return TaskResult(
#             task_id=task_id,
#             status=task["status"],
#             result=task.get("result"),
#             error=task.get("error"),
#     )


@app.get("/task/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    return TaskResult(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error")
    )
