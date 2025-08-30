from library.dbmodules.cmds import list_commands, set_cmd_enabled, get_cmd_enabled
from webpanel.library.auth import require_valid_token, authbook
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
import logging
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@router.get("/ctrl/commands")
async def load_index(request: Request, token: str = Depends(require_valid_token)):
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Has accessed the commands listing page.")
    return templates.TemplateResponse(request, "commands.html")

@router.get("/api/commands/list")
async def list_bot_commands(request: Request, token: str = Depends(require_valid_token)):
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Is getting the list of all the bot commands.")
    all_cmds = list_commands()
    return JSONResponse(
        content={
            "success": True,
            "commands": all_cmds
        },
        status_code=200
    )

@router.get("/api/commands/switch/{cmd_id}")
async def switch_cmd_enabled(request: Request, cmd_id: str, token: str = Depends(require_valid_token)):
    new_status = not get_cmd_enabled(cmd_id)
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Is switching the status of the command {cmd_id} to {new_status}")
    success = set_cmd_enabled(cmd_id, new_status)

    return HTMLResponse(
        content="Success" if success else "Error",
        status_code=200 if success else 500
    )