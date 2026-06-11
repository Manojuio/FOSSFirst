# agents/issue_ranker.py
import json
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="qwen2.5-coder:3b")

def rank_issues(raw_issues):
    """Rank issues by difficulty (1-10) using Qwen. Preserves original fields."""
    print(f"[Ranker] Sending {len(raw_issues)} issues to Qwen...")
    
    # Create a copy with only title + repo + language for prompt (lightweight)
    issues_for_prompt = []
    for iss in raw_issues:
        issues_for_prompt.append({
            "title": iss["title"],
            "repo": iss["repo"],
            "language": iss.get("language", "unknown")
        })
    
    prompt = f"""
You are an issue ranker for open source contributions.
Given these issues, score each from 1 to 10 in difficulty.
1 = trivial (typo, one-line fix, no logic change)
10 = extremely hard (needs deep architecture understanding)

Return ONLY valid JSON in this format:
[
  {{"title": "...", "difficulty": integer, "reason": "short reason"}}
]

Issues:
{json.dumps(issues_for_prompt, indent=2)}
"""
    response = llm.invoke(prompt)
    print("[Ranker] Qwen returned response.")
    
    # Parse JSON
    try:
        start = response.find('[')
        end = response.rfind(']') + 1
        if start != -1 and end != 0:
            json_str = response[start:end]
            ranked = json.loads(json_str)
            print(f"[Ranker] Successfully parsed {len(ranked)} rankings.")
            
            # Merge ranking info back with original raw_issues
            title_to_rank = {r["title"]: r for r in ranked}
            merged = []
            for iss in raw_issues:
                rank_info = title_to_rank.get(iss["title"], {})
                merged.append({
                    **iss,  # keep all original fields
                    "difficulty": rank_info.get("difficulty", 5),
                    "reason": rank_info.get("reason", "No reason provided")
                })
            return merged
    except Exception as e:
        print(f"[Ranker] JSON parsing failed: {e}")
    
    # Fallback: return original issues with default difficulty
    for iss in raw_issues:
        iss["difficulty"] = 5
        iss["reason"] = "Default difficulty (parsing failed)"
    return raw_issues