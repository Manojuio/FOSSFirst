import asyncio
import traceback

import graph as graph_module
from state import State
from backend.utils.job_store import update_job


async def run_graph_job(job_id: str, selected_issue: dict, language: str) -> None:
    try:
        update_job(job_id, status="running")

        initial_state: State = {
            "languages": [language],
            "raw_issues": [selected_issue],
            "ranked_issues": [selected_issue],
            "selected_issue": selected_issue,
            "repo_tree": None,
            "target_files": [],
            "file_contents": {},
            "generated_patch": "",
            "test_results": False,
            "loop_counter": 0,
            "review_feedback": "",
            "final_verdict": "",
        }

        original_interrupt = graph_module.select_issue_interrupt
        graph_module.select_issue_interrupt = lambda ranked_issues: selected_issue
        try:
            graph = graph_module.build_graph()
            final_state = await asyncio.to_thread(graph.invoke, initial_state, {"configurable": {"thread_id": job_id}})
        finally:
            graph_module.select_issue_interrupt = original_interrupt

        result = {
            "selected_issue": final_state.get("selected_issue"),
            "final_verdict": final_state.get("final_verdict"),
            "generated_patch": final_state.get("generated_patch"),
            "review_feedback": final_state.get("review_feedback"),
            "test_results": final_state.get("test_results"),
            "repo_tree": final_state.get("repo_tree"),
        }
        update_job(job_id, status="completed", result=result)
    except Exception as exc:
        update_job(job_id, status="failed", result={"error": str(exc), "traceback": traceback.format_exc()})
