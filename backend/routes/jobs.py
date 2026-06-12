import asyncio

from fastapi import APIRouter, HTTPException

from backend.models.schemas import StartContributionRequest, PrepareContributionResponse
from backend.services.agent_orchestrator import run_graph_job
from backend.utils.job_store import create_job, get_job, jobs
from agents.issue_ranker import rank_issues
from tools.github_api import fetch_beginner_issues

router = APIRouter(prefix="/api/v1/contribution", tags=["contribution"])

session_store: dict[str, list] = {}


@router.post("/prepare")
def prepare_contribution(payload: dict):
    try:
        languages = payload.get("languages", ["python"])
        raw_issues = fetch_beginner_issues(languages, limit_per_lang=3)
        ranked_issues = rank_issues(raw_issues)
        session_id = f"session-{len(session_store) + 1}"
        session_store[session_id] = ranked_issues
        return PrepareContributionResponse(session_id=session_id, ranked_issues=ranked_issues)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to prepare contribution: {exc}") from exc


@router.post("/start")
def start_contribution(payload: StartContributionRequest):
    try:
        if payload.selected_issue is not None:
            selected_issue = payload.selected_issue
            language = payload.language or selected_issue.get("language", "python")
        else:
            if not payload.session_id:
                raise HTTPException(status_code=400, detail="session_id or selected_issue is required")
            ranked_issues = session_store.get(payload.session_id, [])
            if not ranked_issues:
                raise HTTPException(status_code=404, detail="Session not found")
            if not 0 <= payload.selected_issue_index < len(ranked_issues):
                raise HTTPException(status_code=400, detail="selected_issue_index out of range")
            selected_issue = ranked_issues[payload.selected_issue_index]
            language = selected_issue.get("language", "python")

        job_id = create_job("pending")
        asyncio.create_task(run_graph_job(job_id, selected_issue, language))
        return {"job_id": job_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to start contribution: {exc}") from exc


@router.get("/status/{job_id}")
def contribution_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": job["status"], "result": job.get("result")}
