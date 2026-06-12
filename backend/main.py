from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.issues import router as issues_router
from backend.routes.jobs import router as jobs_router
from backend.routes.webhooks import router as webhooks_router
from tools.github_api import get_file_content, get_repo_file_tree

app = FastAPI(title="FOSSFirst API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(issues_router)
app.include_router(jobs_router)
app.include_router(webhooks_router)


@app.get("/api/v1/repositories/{owner}/{repo}/tree")
def repo_tree(owner: str, repo: str):
    try:
        repo_full_name = f"{owner}/{repo}"
        return {"tree": get_repo_file_tree(repo_full_name)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch repo tree: {exc}") from exc


@app.get("/api/v1/repositories/{owner}/{repo}/content")
def repo_content(owner: str, repo: str, path: str):
    try:
        content = get_file_content(f"{owner}/{repo}", path)
        if content is None:
            raise HTTPException(status_code=404, detail="File not found")
        return {"path": path, "content": content}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch file content: {exc}") from exc


@app.get("/")
def health_check():
    return {"status": "ok"}
