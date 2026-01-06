from fastapi.responses import HTMLResponse, JSONResponse
from webpanel.library.auth import authbook, autherrors
from webpanel.library.auth import require_auth
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Primarily used by new users (non-admins) to set their initial password after account creation
@router.get("/set-password/{username}", response_class=HTMLResponse)
async def apifunction(request: Request, username: str, token: str = Depends(require_auth)):
    # Block if they're not account owner. Including admins.
    user = authbook.token_owner(token)
    if not username == user:
        return HTMLResponse("You are not the account owner.", 403)
    return templates.TemplateResponse(request, "password.html")

class PasswordData(BaseModel):
    username: str
    new_password: str

@router.post("/api/users/set-password")
async def register_password(request: Request, data: PasswordData, token: str = Depends(require_auth)):
    # if they're not an admin or the account owner, reject
    user = authbook.token_owner(token)
    if not authbook.user(data.username).is_admin() or user != data.username:
        logging.info(f"Unauthorized password change attempt for user {data.username} from {request.client.host} by {user}")
        return JSONResponse({"success": False, "error": "Unauthorized attempt to change password."}, status_code=403)

    try:
        success = authbook.set_password(
            data.username,
            data.new_password,
        )
    except autherrors.UserNotFound:
        return JSONResponse({"success": False, "error": "User not found."}, status_code=404)

    logging.info(f"Password for user {data.username} set successfully by {request.client.host}")
    return JSONResponse(content={'success': success}, status_code=200 if success is True else 500)