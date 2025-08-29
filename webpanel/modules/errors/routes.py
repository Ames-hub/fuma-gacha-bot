from library.dbmodules.bugsdb import list_bug_reports, get_bug_report, mark_bug_report_unresolved, mark_bug_report_resolved
from webpanel.library.auth import require_valid_token, authbook
from library.dbmodules.shared import update_user_on_bug
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import datetime
import logging
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@router.get("/bot/errors")
async def load_index(request: Request, token: str = Depends(require_valid_token)):
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Has accessed the error reports page.")

    all_reports = list_bug_reports()

    total_reports = 0
    open_bug_reports = []
    closed_bug_reports = []
    for report in all_reports:
        if report["resolved"] is False:
            open_bug_reports.append(report)
        else:
            # Only show reports that were closed less than 30 days ago.
            if datetime.datetime.strptime(report["report_date"], "%Y-%m-%d %H:%M:%S") > datetime.datetime.now() - datetime.timedelta(days=30):
                closed_bug_reports.append(report)
        total_reports += 1

    return templates.TemplateResponse(request, "index.html", {
        "open": len(open_bug_reports),
        "closed": len(closed_bug_reports),
        "total_reports": total_reports,
    })

@router.get("/bot/errors/{error_id}")
async def load_error(request: Request, error_id: int, token: str = Depends(require_valid_token)):
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Has accessed the error report {error_id}.")
    report = get_bug_report(bugid=error_id)
    status = "open" if bool(report['resolved']) is False else "closed"

    return templates.TemplateResponse(request, "error.html", {
        "bug": {
            "id": error_id,
            "title": report['stated_bug'],
            "status": status,
            "severity": report['severity'],
            "reported_by": report['reporter_id'],
            "date_reported": report['report_date'],
            "reproduction": report['reproduction_steps'],
            "additional_info": report['extra_info'],
            "problem_section": report['problem_section'],
            "expected_result": report['expected_result'],
        }
    })

@router.get("/api/errors/list")
async def list_errors(request: Request, token: str = Depends(require_valid_token)):
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Is listing the error reports.")

    all_errors = list_bug_reports()

    parsed_data = []
    for error in all_errors:
        parsed_data.append({
            "id": error["bugid"],
            "title": error["stated_bug"],
            "status": "open" if bool(error["resolved"]) is False else "closed",
            "severity": error['severity']
        })

    return parsed_data

class ResolveData(BaseModel):
    bug_id: int
    response: str

@router.post("/api/errors/resolve")
async def resolve_error(request: Request, data: ResolveData, token: str = Depends(require_valid_token)):
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Is closing the error report {data.bug_id}.")
    success = mark_bug_report_resolved(data.bug_id)

    if success:
        await update_user_on_bug(data.bug_id, data.response)
        logging.info(
            f"IP {request.client.host} ({authbook.token_owner(token)}) Has resolved the error report {data.bug_id} and notified the user with the response: {data.response}"
        )

    return HTMLResponse(
        content="Successfully resolved bug and notified user!" if success else "Error resolving bug and notifying user!",
        status_code=200 if success else 500
    )

class UnresolveData(BaseModel):
    bug_id: int

@router.post("/api/errors/unresolve")
async def resolve_error(request: Request, data: UnresolveData, token: str = Depends(require_valid_token)):
    logging.info(f"IP {request.client.host} ({authbook.token_owner(token)}) Is re-opening the error report {data.bug_id}.")
    success = mark_bug_report_unresolved(data.bug_id)
    return HTMLResponse(content="Success" if success else "Error", status_code=200 if success else 500)