# final_report.py
def generate_report(state: dict) -> str:
    """
    Generate a final report from the current state.
    Returns a formatted string with summary and verdict.
    """
    print("[FinalReport] Generating final summary...")
    
    issue = state.get("selected_issue", {})
    patch = state.get("generated_patch", "")
    test_result = state.get("test_results", False)
    review = state.get("review_feedback", "")
    loop_counter = state.get("loop_counter", 0)
    
    # Determine verdict
    if test_result and "VERDICT: ready to submit" in review:
        verdict = "✅ READY TO SUBMIT – The patch passes tests and maintainer approval."
    elif test_result and "VERDICT: needs revision" in review:
        verdict = "⚠️ NEEDS REVISION – Patch passes tests but maintainer requests changes."
    elif not test_result:
        verdict = "❌ PATCH FAILED – Tests failed after multiple attempts. Requires manual fix."
    else:
        verdict = "🤔 UNCLEAR – Review manually."
    
    # Build report
    report = f"""
{'='*60}
FOSSFirst – FINAL CONTRIBUTION REPORT
{'='*60}

ISSUE:
  Title: {issue.get('title', 'N/A')}
  Repo: {issue.get('repo', 'N/A')}
  URL: {issue.get('url', 'N/A')}
  Language: {issue.get('language', 'N/A')}

PATCH:
  Length: {len(patch)} characters
  Preview:
{patch[:500]}{'...' if len(patch) > 500 else ''}

TESTS:
  Result: {'PASSED' if test_result else 'FAILED'}
  Attempts: {loop_counter + 1 if test_result else loop_counter}/3

MAINTAINER REVIEW:
{review[:800]}{'...' if len(review) > 800 else ''}

{'='*60}
VERDICT: {verdict}
{'='*60}

Next steps:
  - If ready: submit the patch as a pull request to {issue.get('repo', 'the repository')}.
  - If needs revision: address the maintainer's comments and re-run FOSSFirst.
  - If failed: manually inspect the issue and file.

Thank you for using FOSSFirst!
"""
    print("[FinalReport] Report generated.")
    return report