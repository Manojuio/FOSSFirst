# agents/codebase_mapper.py
import json
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="qwen2.5-coder:3b")

def map_codebase(issue: dict, repo_tree: list):
    """
    Given an issue and a repository file tree,
    return a list of likely file paths that need to be edited.
    """
    print(f"[Mapper] Analyzing issue: {issue.get('title')}")
    print(f"[Mapper] Repo tree has {len(repo_tree)} items.")
    
    # Prepare a simplified tree description for the LLM
    tree_summary = []
    for item in repo_tree:
        tree_summary.append(f"{item['type']}: {item['path']}")
    tree_text = "\n".join(tree_summary[:50])  # limit to avoid huge prompts
    
    prompt = f"""
You are a codebase mapper. Given an issue and a repository file tree, identify the 1-3 most relevant file paths.

Issue title: {issue.get('title')}
Issue body preview: {issue.get('body_preview', '')}

Repository file tree (simplified):
{tree_text}

Rules:
- If the issue is about documentation (e.g., "add section", "update README"), prioritize .md files and docs/ folder.
- If it's about code changes (e.g., "fix typo in error message"), prioritize .py files.
- Only suggest files that exist in the tree above.

Return ONLY JSON: {{"target_files": ["path1", "path2"], "reasoning": "..."}}
"""
    response = llm.invoke(prompt)
    print("[Mapper] Qwen returned mapping.")
    
    # Parse JSON response
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = response[start:end]
            result = json.loads(json_str)
            target_files = result.get("target_files", [])
            reasoning = result.get("reasoning", "")
            print(f"[Mapper] Suggested {len(target_files)} file(s): {target_files}")
            print(f"[Mapper] Reasoning: {reasoning}")
            return target_files
    except Exception as e:
        print(f"[Mapper] JSON parsing failed: {e}")
    
    # Fallback: empty list
    return []