import time
import uuid
from typing import Dict, Optional

jobs: Dict[str, Dict[str, object]] = {}


def create_job(status: str = "pending") -> str:
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": status,
        "result": None,
        "created_at": time.time(),
    }
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, object]]:
    return jobs.get(job_id)


def update_job(job_id: str, **kwargs) -> Dict[str, object]:
    job = jobs.get(job_id)
    if not job:
        raise KeyError("job not found")
    job.update(kwargs)
    return job
