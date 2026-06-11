# state.py
from typing import TypedDict, List, Dict, Optional, Any

class State(TypedDict):
    # Input
    languages: List[str]
    
    # GitHub fetcher output
    raw_issues: List[Dict]
    
    # Ranker output
    ranked_issues: List[Dict]
    
    # Human selection
    selected_issue: Optional[Dict]
    
    # Codebase Mapper
    repo_tree: Optional[List[Dict]]
    target_files: List[str]
    
    # Content & Patch
    file_contents: Dict[str, str]
    generated_patch: str
    test_results: bool
    loop_counter: int
    
    # Maintainer & Final
    review_feedback: str
    final_verdict: str