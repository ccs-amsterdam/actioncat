import logging

from fastapi import FastAPI, Query, Body, Request
from queue import Queue
from typing import Optional, List
from pydantic import BaseModel
from pydantic.config import Extra

from kittens import wake
from amcat import request_documents

app = FastAPI(
    title="actionherder"
)

bowl = Queue()

class settings(BaseModel):
    n_kittens: int = 1
    
    class Config:
        extra = Extra.allow


class token(BaseModel):
    host: str
    bearer: str
    
    class Config:
        extra = Extra.allow
    
class action(BaseModel):
    
    class Config:
        extra = Extra.allow

    
@app.post("/jobs")
def receive_job(index: str,
                ids: List[str],
                action: dict = Body("", description="A docker compose json string"),
                settings: settings = Body({"n_kittens": 1}, description="Number of kittens (n_kittens) "
                                                             "and other parameters passed to kittens"),
                token: dict = Body({"host": "http://localhost/amcat"}, 
                                    description="if required by amcat instance, "
                                                "a dict with access_token and host")):
    """
    Receives the job description from actioncat with:
    - index
    - IDs
    - action
    - workflow settings
    - token

    Returns a list of dicts containing name, role, and guest attributes
    """
    # fill bowl for kittens
    # TODO: what to do if new ids should be added to the index with an action?
    for item in request_documents(index, ids, token):
        bowl.put(item)

    logging.info("bowl filled")

    # wake up kittens
    wake(action, settings)

    return {"status": f"{settings.n_kittens} kittens are feeding now on {bowl.qsize()} jobs"}


@app.get("/bowl/")
async def get_next_document():
    if not bowl.empty():
        logging.info(bowl.qsize())
        return bowl.get()
    else:
        return {"status": "sleepy kitty"}
