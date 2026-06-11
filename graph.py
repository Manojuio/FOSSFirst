# graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from state import State
from tools.github_api import fetch_beginner_issues, get_repo_file_tree, get_file_content, get_repo_contributing_guidelines
from agents.issue_ranker import rank_issues
from agents.codebase_mapper import map_codebase
from agents.patch_writer import write_patch
from tools.sandbox import apply_patch_and_test
from agents.maintainer_simulator import simulate_review
from final_report import generate_report
from ui.cli import select_issue_interrupt

MAX_LOOP = 3

# ----- Node functions -----

def node_fetch_issues(state: State) -> State:
    print("[Graph] Node: Fetch Issues")
    issues = fetch_beginner_issues(state["languages"], limit_per_lang=3)
    state["raw_issues"] = issues
    return state

def node_rank_issues(state: State) -> State:
    print("[Graph] Node: Rank Issues")
    if not state.get("raw_issues"):
        return state
    ranked = rank_issues(state["raw_issues"])
    state["ranked_issues"] = ranked
    return state

def node_human_select(state: State) -> State:
    print("[Graph] Node: Human Select (interrupt)")
    if not state.get("ranked_issues"):
        return state
    selected = select_issue_interrupt(state["ranked_issues"])
    state["selected_issue"] = selected
    return state

def node_get_tree(state: State) -> State:
    print("[Graph] Node: Get Repo Tree")
    if not state.get("selected_issue"):
        return state
    repo = state["selected_issue"]["repo"]
    tree = get_repo_file_tree(repo)
    state["repo_tree"] = tree
    return state

def node_map_codebase(state: State) -> State:
    print("[Graph] Node: Map Codebase")
    if not state.get("selected_issue") or not state.get("repo_tree"):
        return state
    target = map_codebase(state["selected_issue"], state["repo_tree"])
    state["target_files"] = target
    return state

def node_fetch_content(state: State) -> State:
    print("[Graph] Node: Fetch Content")
    if not state.get("target_files") or not state.get("selected_issue"):
        return state
    repo = state["selected_issue"]["repo"]
    first_file = state["target_files"][0]
    content = get_file_content(repo, first_file)
    if not content:
        # fallback to README.md
        content = get_file_content(repo, "README.md")
        if content:
            first_file = "README.md"
            state["target_files"] = [first_file]
    if content:
        state["file_contents"] = {first_file: content}
    return state

def node_write_patch(state: State) -> State:
    print("[Graph] Node: Write Patch")
    if not state.get("file_contents") or not state.get("selected_issue"):
        return state
    file_path = list(state["file_contents"].keys())[0]
    content = state["file_contents"][file_path]
    patch = write_patch(state["selected_issue"], file_path, content)
    state["generated_patch"] = patch
    return state

def node_test_patch(state: State) -> State:
    print("[Graph] Node: Test Patch")
    if not state.get("file_contents") or not state.get("generated_patch"):
        return state
    file_path = list(state["file_contents"].keys())[0]
    content = state["file_contents"][file_path]
    success, _ = apply_patch_and_test(content, state["generated_patch"], file_path)
    state["test_results"] = success
    return state

def node_fetch_guidelines(state: State) -> State:
    print("[Graph] Node: Fetch Guidelines")
    if not state.get("selected_issue"):
        return state
    repo = state["selected_issue"]["repo"]
    guidelines = get_repo_contributing_guidelines(repo)
    # Store guidelines in state temporarily (we can add a field, but we'll just pass through)
    state["review_feedback"] = guidelines  # reuse field temporarily
    return state

def node_simulate_maintainer(state: State) -> State:
    print("[Graph] Node: Simulate Maintainer")
    if not state.get("selected_issue") or not state.get("generated_patch"):
        return state
    guidelines = state.get("review_feedback")
    review = simulate_review(state["selected_issue"], state["generated_patch"], guidelines)
    state["review_feedback"] = review
    return state

def node_final_report(state: State) -> State:
    print("[Graph] Node: Final Report")
    report = generate_report(state)
    print(report)
    # Extract verdict from report
    if "✅ READY TO SUBMIT" in report:
        state["final_verdict"] = "ready to submit"
    elif "⚠️ NEEDS REVISION" in report:
        state["final_verdict"] = "needs revision"
    else:
        state["final_verdict"] = "uncertain"
    return state

# ----- Conditional edge for test retry -----
def should_retry_patch(state: State) -> str:
    if state.get("test_results"):
        return "pass"
    elif state.get("loop_counter", 0) < MAX_LOOP - 1:
        state["loop_counter"] = state.get("loop_counter", 0) + 1
        return "retry"
    else:
        return "fail"

# ----- Build the graph -----
def build_graph():
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("fetch_issues", node_fetch_issues)
    workflow.add_node("rank_issues", node_rank_issues)
    workflow.add_node("human_select", node_human_select)
    workflow.add_node("get_tree", node_get_tree)
    workflow.add_node("map_codebase", node_map_codebase)
    workflow.add_node("fetch_content", node_fetch_content)
    workflow.add_node("write_patch", node_write_patch)
    workflow.add_node("test_patch", node_test_patch)
    workflow.add_node("fetch_guidelines", node_fetch_guidelines)
    workflow.add_node("simulate_maintainer", node_simulate_maintainer)
    workflow.add_node("final_report", node_final_report)
    
    # Define edges
    workflow.set_entry_point("fetch_issues")
    workflow.add_edge("fetch_issues", "rank_issues")
    workflow.add_edge("rank_issues", "human_select")
    workflow.add_edge("human_select", "get_tree")
    workflow.add_edge("get_tree", "map_codebase")
    workflow.add_edge("map_codebase", "fetch_content")
    workflow.add_edge("fetch_content", "write_patch")
    workflow.add_edge("write_patch", "test_patch")
    
    # Conditional edge from test_patch
    workflow.add_conditional_edges(
        "test_patch",
        should_retry_patch,
        {
            "retry": "write_patch",   # loop back
            "pass": "fetch_guidelines",
            "fail": "final_report"    # skip maintainer if max retries reached
        }
    )
    
    workflow.add_edge("fetch_guidelines", "simulate_maintainer")
    workflow.add_edge("simulate_maintainer", "final_report")
    workflow.add_edge("final_report", END)
    
    # Compile with memory checkpoint (for human interrupt)
    memory = InMemorySaver()
    graph = workflow.compile(checkpointer=memory)
    return graph