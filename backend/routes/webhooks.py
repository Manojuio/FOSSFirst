from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/github")
async def github_webhook(request: Request):
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
    return {"received": True, "payload": payload}
