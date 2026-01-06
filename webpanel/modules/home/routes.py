from webpanel.library.auth import require_auth, authbook
from library.database import dbcards, stdn_events, lmtd_events
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
import logging
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@router.get("/")
async def load_index(request: Request, token: str = Depends(require_auth)):
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Has accessed the home page.")

    all_cards = dbcards.list_all()
    card_count = len(all_cards)
    pullable_count = 0
    for card in all_cards:
        if card['pullable'] is True:
            pullable_count += 1

    all_active_events = stdn_events.get_all_events(active_only=True)
    all_active_lim_events = lmtd_events.get_all_events(active_only=True)

    return templates.TemplateResponse(request, "index.html", {
        "cards": {
            "count": card_count,
            "pullable_count": pullable_count,
        },
        "events": {
            "stn_active_count": len(all_active_events),
            "lim_active_count": len(all_active_lim_events)
        }
    })