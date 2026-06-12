from fastapi import APIRouter, HTTPException

from agents.issue_ranker import rank_issues
from backend.models.schemas import FetchIssuesRequest, RankIssuesRequest
from tools.github_api import fetch_beginner_issues

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])


@router.post("/fetch")
def fetch_issues(payload: FetchIssuesRequest):
    try:
        issues = fetch_beginner_issues(payload.languages, limit_per_lang=3)
        return {"issues": issues}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch issues: {exc}") from exc


@router.post("/rank")
def rank_issues_endpoint(payload: RankIssuesRequest):
    try:
        if not payload.raw_issues:
            raise ValueError("raw_issues cannot be empty")
        ranked = rank_issues(payload.raw_issues)
        return {"ranked_issues": ranked}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
