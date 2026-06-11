# main.py
import sys
from dotenv import load_dotenv
from state import State
from graph import build_graph

load_dotenv()

def main():
    print("\n" + "="*60)
    print("FOSSFirst – Open Source Contribution Navigator")
    print("="*60 + "\n")
    
    # Initial state
    initial_state: State = {
        "languages": ["python"],
        "raw_issues": [],
        "ranked_issues": [],
        "selected_issue": None,
        "repo_tree": None,
        "target_files": [],
        "file_contents": {},
        "generated_patch": "",
        "test_results": False,
        "loop_counter": 0,
        "review_feedback": "",
        "final_verdict": ""
    }
    
    # Build and run graph
    graph = build_graph()
    
    # Use a thread ID for checkpointing (enables interrupt/resume)
    config = {"configurable": {"thread_id": "1"}}
    
    try:
        final_state = graph.invoke(initial_state, config=config)
        print("\n✅ FOSSFirst finished. Final verdict:", final_state.get("final_verdict"))
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()