import shutil
from typing import List, Optional
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse, HTMLResponse
import os
import sys
import datetime

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from lib import ROOT_DIR
from lib.conversation_block import Conversation, ConversationBlock
from lib.browser_util import get_active_browser_content, split_app_content
from lib.custom_logger import get_custom_logger
from webapp.backend_utils import map_config

logger = get_custom_logger(__file__, "app", add_date=False, console=True)

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


class Content(BaseModel):
    content: str
    area: str


def get_config(old_cfg=None):
    if old_cfg:
        now = datetime.datetime.now()
        prev = old_cfg.get("last_update", datetime.datetime.now())
        if (now - prev) < datetime.timedelta(seconds=1):
            return old_cfg
    with open("config.txt") as file:
        APP_CONFIG = map_config(file.read())
        APP_CONFIG["last_update"] = datetime.datetime.now()
        return APP_CONFIG


APP_CONFIG = get_config()
# logger.debug(APP_CONFIG)


@app.get("/")
async def root():
    return FileResponse(os.path.join(WEBAPP_PATH, "index.html"))


@app.get("/{file}")
async def get_specific_file(file: str):
    if file in ["index.html", "script.js", "style.css"]:
        file_path = os.path.join(WEBAPP_PATH, file)
        try:
            return FileResponse(file_path)
        except FileNotFoundError:
            logger.error(f"File not found: file")
            return HTMLResponse(content="<h1>File not found</h1>", status_code=404)


@app.post("/api/v1/update_textarea_content/")
async def update_textarea_content(content: Content):
    logger.debug(f"update: {content}")
    if content.area in APP_CONFIG.get("files", {}).keys():
        path = os.path.join(ROOT_DIR, APP_CONFIG["files"][content.area])
        shutil.move(path, path + ".bak")
        with open(path, "w", encoding="UTF-8") as file:
            file.write(content.content)
    return


@app.post("/api/v1/update_config/")
async def update_textarea_content(content: Content):
    global APP_CONFIG
    logger.debug(f"update: {content}")
    if content.area == "textarea_config":
        _cfg = map_config(content.content)
        for k, v in _cfg.get("files", {}).items():
            if os.path.exists(os.path.join(ROOT_DIR, v)):
                APP_CONFIG["files"][k] = v
        APP_CONFIG["last_update"] = datetime.datetime.now()

        logger.info(APP_CONFIG)
    return


@app.get("/api/v1/get_textarea_content/{area}")
async def get_textarea_content(area: str):
    global APP_CONFIG
    logger.debug(f"get_textarea_content {area}")
    if not area in APP_CONFIG.get("files", {}).keys():
        return Response(content="", media_type="text/plain")
    try:
        config = get_config(APP_CONFIG)
        path = os.path.join(ROOT_DIR, config["files"][area])
        with open(path, "r", encoding="UTF-8") as file:
            contents = file.read()
            # logger.debug(contents)
        if area == "textarea_config":
            APP_CONFIG = map_config(contents)
            logger.info(APP_CONFIG)

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
