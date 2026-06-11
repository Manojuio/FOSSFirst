# agents/patch_writer.py (updated)
import json
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="qwen2.5-coder:3b")

def write_patch(issue: dict, file_path: str, file_content: str):
    """Generate a unified diff/patch."""
    print(f"[PatchWriter] Generating patch for {file_path}")
    
    # Truncate content if too long
    content_preview = file_content[:4000]
    
    prompt = f"""You are a helpful coding assistant. Generate a unified diff (patch) to fix this issue.

ISSUE: {issue['title']}
DESCRIPTION: {issue.get('body_preview', '')}

FILE: {file_path}
CONTENT:
TASK: Output ONLY a valid unified diff that applies the fix. Use the standard diff format:
--- a/{file_path}
+++ b/{file_path}
@@ -line,count +line,count @@
- old line
+ new line

Do NOT include any explanations, JSON, or extra text. Only the diff."""
    
    response = llm.invoke(prompt)
    # Clean up: remove any markdown code fences if present
    patch = response.strip()
    if patch.startswith("```diff"):
        patch = patch[7:]
    if patch.startswith("```"):
        patch = patch[3:]
    if patch.endswith("```"):
        patch = patch[:-3]
    patch = patch.strip()
    print("[PatchWriter] Patch generated.")
    return patch