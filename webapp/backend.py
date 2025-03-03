from typing import List, Optional
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import os
import sys

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from lib import ROOT_DIR
from lib.conversation_block import Conversation, ConversationBlock
from lib.browser_util import get_active_browser_content, split_app_content
from lib.custom_logger import get_custom_logger

logger = get_custom_logger(__file__, "app", add_date=True, console=True)

WEBAPP_PATH = os.path.join(parent_dir, "webapp")
DEBUG = True

app = FastAPI(debug=DEBUG)

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "http://localhost:8000",
    "localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    text: str


class ConversationBlockModel(BaseModel):
    name: str
    text: str


@app.get("/")
async def root():
    try:
        with open(os.path.join(WEBAPP_PATH, "index.html"), "r", encoding="UTF-8") as file:
            html_content = file.read()
            return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        logger.error(f"File not found: index.html")
        return HTMLResponse(content="<h1>File not found</h1>", status_code=404)


@app.post("/api/v1/update_textarea1_content/")
async def update_textarea_content(content: Optional[str] = None):
    logger.debug(content)


@app.get("/api/v1/get_textarea1_content")
async def get_textarea1_content():
    logger.debug("get_textarea1_content")

    try:
        path = os.path.join(ROOT_DIR, "pinned.txt")
        with open(path, "r", encoding="UTF-8") as file:
            contents = file.read()
            logger.debug(contents)
            return Response(content=contents, media_type="text/plain")
    except Exception as ex:
        logger.error(ex)
        raise


@app.get("/api/v1/get_browser_content")
async def get_browser_content() -> List[ConversationBlockModel]:
    content = get_active_browser_content()
    blocks = split_app_content(content, app="chatgpt")
    conversation = Conversation()
    for name, text, index in blocks:
        conversation.append(ConversationBlock(name, text, index))

    # Convert ConversationBlock objects to ConversationBlockModel
    return [
        ConversationBlockModel(name=block.name, text=block.text) for block in conversation.blocks
    ]


@app.post("/api/v1/message")
async def post_message(message: Message):
    print(message.text)
    return {"message": message.text}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
