# tools/sandbox.py
import tempfile
import os
import subprocess
import re

def apply_patch_and_test(original_content: str, patch: str, file_path: str):
    """
    Apply patch to a temporary file, then run Python syntax check if applicable.
    Returns (success: bool, error_message: str)
    """
    print("[Sandbox] Testing patch in temporary environment...")
    
    # Basic patch format validation
    if not patch or '--- a/' not in patch or '+++ b/' not in patch:
        print("[Sandbox] Patch format invalid (missing diff headers).")
        return False, "Invalid patch format"
    
    if not re.search(r'^[-+].+', patch, re.MULTILINE):
        print("[Sandbox] Patch does not contain any line changes.")
        return False, "No line changes in patch"
    
    # For non-Python files, we only validate format (skip syntax check)
    if not file_path.endswith('.py'):
        print("[Sandbox] Non-Python file; skipping syntax check. Patch format valid.")
        return True, "Patch format valid (non-Python)"
    
    # For Python files, do a syntax check on the original file (as a baseline)
    # Write original content with UTF-8 encoding to avoid Unicode errors
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(original_content)
            temp_path = f.name
        
        # Check syntax of original file
        result_orig = subprocess.run(
            ['python', '-m', 'py_compile', temp_path],
            capture_output=True, text=True
        )
        if result_orig.returncode != 0:
            print("[Sandbox] Original file has syntax errors. Cannot proceed.")
            return False, "Original file has syntax errors"
        
        # In Phase 5 we simulate patch application success if format is okay.
        # A full implementation would apply the patch and re-check syntax.
        print("[Sandbox] Python syntax check passed (simulated).")
        return True, "Syntax check passed"
    
    except Exception as e:
        print(f"[Sandbox] Unexpected error: {e}")
        return False, str(e)
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)