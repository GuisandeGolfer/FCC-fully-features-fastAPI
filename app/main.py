from app.schemas import DownloadRequest, TaskResponse, TaskStatus, TaskResult
from fastapi import FastAPI, HTTPException
import asyncio
import uuid
from typing import Dict
from concurrent.futures import ProcessPoolExecutor
from app.claude_youtube_sum import process_youtube_summary

app = FastAPI()

# TODO: add sqllite database, or maybe spin up a postgres container and test functionality.
    # sqlite3 would not be a good idea because it does not handle multiple readers and writers well.
task_queue = asyncio.Queue()

tasks: Dict[str, Dict] = {}

# ProcessPoolExecutor for running CPU-bound tasks
process_pool = ProcessPoolExecutor()

async def worker():
    while True:
        task_id, url, detail = await task_queue.get()
        tasks[task_id]["status"] = TaskStatus.IN_PROGRESS

        await start_prompt_process(task_id, url, detail)

        task_queue.task_done()

# create 10 asyncio worker threads
@app.on_event("startup")
async def startup_event():
    # Start workers
    for _ in range(10):
        asyncio.create_task(worker())


async def start_prompt_process(task_id: str, url: str, detail: str):
    try:
        result = await process_youtube_summary(url, detail)
        if result['status'] == TaskStatus.COMPLETED:
            tasks[task_id]["result"] = result["summary"]
    except Exception as e:
        tasks[task_id]["status"] = TaskStatus.FAILED # This 'try' statement keeps failing.
        tasks[task_id]["error"] = str(e)


@app.post("/start-download", response_model=TaskResponse)
async def start_download(request: DownloadRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": TaskStatus.PENDING}

    await task_queue.put((task_id, request.url, request.detail_level))
    return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)


@app.get("/task/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    if task_id not in [task_id for task_id in tasks]:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    return TaskResult(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error")
    )
