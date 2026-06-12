from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FetchIssuesRequest(BaseModel):
    languages: List[str] = Field(default_factory=lambda: ["python"])


class RankIssuesRequest(BaseModel):
    raw_issues: List[Dict[str, Any]]


class PrepareContributionRequest(BaseModel):
    languages: List[str] = Field(default_factory=lambda: ["python"])


class StartContributionRequest(BaseModel):
    session_id: Optional[str] = None
    selected_issue_index: int = 0
    selected_issue: Optional[Dict[str, Any]] = None
    language: Optional[str] = None


class JobStatusResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None


class PrepareContributionResponse(BaseModel):
    session_id: str
    ranked_issues: List[Dict[str, Any]]


class StartContributionResponse(BaseModel):
    job_id: str
