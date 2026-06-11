# ui/cli.py
def select_issue_interrupt(ranked_issues):
    """
    Pause and ask user to select an issue from ranked list.
    Returns the selected issue dict.
    """
    print("\n" + "="*60)
    print("📋 RANKED ISSUES (easiest first)")
    print("="*60)
    
    # Sort by difficulty for display
    sorted_issues = sorted(ranked_issues, key=lambda x: x.get("difficulty", 10))
    
    for idx, issue in enumerate(sorted_issues, start=1):
        print(f"{idx}. {issue.get('title')}")
        print(f"   Difficulty: {issue.get('difficulty')}/10")
        print(f"   Reason: {issue.get('reason')}")
        print(f"   Repo: {issue.get('repo', 'unknown')}")
        print(f"   Language: {issue.get('language', 'unknown')}\n")
    
    while True:
        try:
            choice = input("🔍 Enter the number of the issue you want to work on: ")
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(sorted_issues):
                selected = sorted_issues[choice_idx]
                print(f"\n✅ Selected: {selected['title']}\n")
                return selected
            else:
                print(f"Please enter a number between 1 and {len(sorted_issues)}")
        except ValueError:
            print("Invalid input. Please enter a number.")