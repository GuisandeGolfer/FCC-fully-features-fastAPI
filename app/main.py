from app.schemas import DownloadRequest, TaskResponse, TaskStatus, TaskResult
from fastapi import FastAPI, HTTPException
import asyncio
import uuid
import logging
from typing import Dict
from concurrent.futures import ProcessPoolExecutor
from app.claude_youtube_sum import process_youtube_summary

app = FastAPI()

# TODO: add sqllite database, or maybe spin up a postgres container and test functionality.
task_queue = asyncio.Queue()

tasks: Dict[str, Dict] = {}

process_pool = ProcessPoolExecutor()

async def worker():
    while True:
        task_id, url, detail = await task_queue.get()
        try:
            tasks[task_id]["status"] = TaskStatus.IN_PROGRESS
            await start_prompt_process(task_id, url, detail)
        except Exception as e:
            logging.exception(f"Worker error for task {task_id}: {e}")
            tasks[task_id]["status"] = TaskStatus.FAILED
            tasks[task_id]["error"] = str(e)
        finally:
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
        # Ensure 'result' contains the expected keys
        if result != None:
            tasks[task_id]["summary"] = result
            tasks[task_id]["status"] = TaskStatus.COMPLETED  # Update status
        else:
            tasks[task_id]["status"] = TaskStatus.FAILED  # Update status
        tasks[task_id]["status"] = TaskStatus.COMPLETED  # Update status
    except Exception as e:
        logging.exception(f"Error processing task {task_id}: {e}")
        tasks[task_id]["status"] = TaskStatus.FAILED
        tasks[task_id]["error"] = str(e)


@app.post("/start-download", response_model=TaskResponse)
async def start_download(request: DownloadRequest):
    # create a unique task id
    task_id = str(uuid.uuid4())

    #hello
    tasks[task_id] = {"status": TaskStatus.PENDING}

    await task_queue.put((task_id, request.url, request.detail_level))

    return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)


@app.get("/task/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    if task_id not in [task_id for task_id in tasks]:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]

    print(task)

    return TaskResult(
        task_id=task_id,
        status=task["status"],
        summary=task.get("summary"),
        error=task.get("error")
    )
