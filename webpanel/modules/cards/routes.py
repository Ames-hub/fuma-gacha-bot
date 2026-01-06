from webpanel.library.perms import require_permissions, permissions
from webpanel.library.auth import require_auth, authbook
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from library.dbmodules import dbcards
from pydantic import BaseModel
import logging
import base64
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@router.get("/cards", response_class=HTMLResponse)
@require_permissions(permissions.MANAGE_CARDS)
async def show_reg(request: Request, token: str = Depends(require_auth)):
    logging.info(f"User {authbook.token_owner(token)} has accessed the cards page. Host: {request.client.host}")
    return templates.TemplateResponse(request, "cardlist.html")

@require_permissions(permissions.MANAGE_CARDS)
@router.get("/cards/{card_id}")
async def show_card(request: Request, card_id:str, token: str = Depends(require_auth)):
    logging.info(f"User {authbook.token_owner(token)} is accessing card {card_id} on the WebAPI. Host: {request.client.host}")
    card = dbcards.view_card(name=card_id)[0]

    img_base64 = base64.b64encode(card['img_bytes']).decode('utf-8')
    card['img_bytes'] = img_base64

    return templates.TemplateResponse(request, "cardview.html", {
        "card": card
    })

@router.get("/api/cards/view/{card_id}")
@require_permissions(permissions.MANAGE_CARDS)
async def get_card(request: Request, card_id:str, token: str = Depends(require_auth)):
    card = dbcards.view_card(name=card_id)[0]

    if not card:
        return HTMLResponse(
            content="Card not found.",
            status_code=404
        )

    img_base64 = base64.b64encode(card['img_bytes']).decode('utf-8')
    card['img_bytes'] = img_base64

    logging.info(f"User {authbook.token_owner(token)} has accessed card {card_id} on the WebAPI. Host: {request.client.host}")
    return JSONResponse(
        content=card,
        status_code=200
    )

@router.get("/api/cards/list")
@require_permissions(permissions.MANAGE_CARDS)
async def get_cards(request: Request, token: str = Depends(require_auth)):
    cards = dbcards.list_all()
    logging.info(f"User {authbook.token_owner(token)} has listed all cards on the WebAPI. Host: {request.client.host}")
    success = cards != False
    return JSONResponse(
        content={
            'success': success,
            'cards': cards
        },
        status_code=200 if success is True else 500
    )

class DelCardData(BaseModel):
    id: str

@router.post("/api/cards/delete")
@require_permissions(permissions.MANAGE_CARDS)
async def del_card(request: Request, data: DelCardData, token: str = Depends(require_auth)):
    success = dbcards.rm_card(data.id)
    logging.info(f"User {authbook.token_owner(token)} has deleted card {data.id} from the WebAPI. Host: {request.client.host}")
    return JSONResponse(
        content={
            'success': success
        },
        status_code=200 if success is True else 500
    )

class PullableData(BaseModel):
    card_id: str

@router.post("/api/cards/set_pullable")
@require_permissions(permissions.MANAGE_CARDS)
async def set_pullable(request: Request, data: PullableData, token: str = Depends(require_auth)):
    if dbcards.check_exists(data.card_id) is False:
        return HTMLResponse(
            content="Card not found.",
            status_code=404
        )

    card = dbcards.view_card(name=data.card_id)[0]
    currently_pullable = card['pullable']
    pullable = not currently_pullable

    logging.info(f"User {authbook.token_owner(token)} has flipped the pullability of card {data.card_id} tp {pullable}. Host: {request.client.host}")

    success = dbcards.set_pullability(
        card_id=data.card_id,
        value=pullable
    )

    return HTMLResponse(
        content="Success!" if success is True else "Error.",
        status_code=200 if success is True else 500
    )

@router.get("/api/cards/{card_id}")
@require_permissions(permissions.MANAGE_CARDS)
async def manage_card(request: Request, card_id:str, token: str = Depends(require_auth)):
    logging.info(f"User {authbook.token_owner(token)} is accessing/managing card {card_id} on the WebAPI. Host: {request.client.host}")