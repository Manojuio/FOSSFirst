# agents/maintainer_simulator.py
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="qwen2.5-coder:3b")

def simulate_review(issue: dict, patch: str, contributing_guidelines: str = None):
    """
    Simulate a maintainer's review of the patch.
    Returns a string with feedback.
    """
    print("[Simulator] Running maintainer simulation...")
    
    guidelines_text = contributing_guidelines if contributing_guidelines else "No CONTRIBUTING.md found. Use common open‑source best practices."
    
    prompt = f"""
You are a strict but fair open‑source maintainer. Review the following patch for the given issue.

ISSUE TITLE: {issue['title']}
ISSUE DESCRIPTION: {issue.get('body_preview', '')}

CONTRIBUTING GUIDELINES:
{guidelines_text[:1500]}

PATCH:
{patch[:2000]}

Answer these questions in your review:
1. Does the patch correctly address the issue? (yes/no/partial)
2. Does it follow the project's coding standards? (yes/no/explain)
3. Are there missing tests or documentation updates?
4. Any other concerns (e.g., performance, edge cases)?

Format your response as:
REVIEW:
[detailed feedback]
VERDICT: [ready to submit / needs revision / rejected]
"""
    
    response = llm.invoke(prompt)
    print("[Simulator] Review generated.")
    return response.strip()