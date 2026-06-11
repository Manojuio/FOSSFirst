# tools/github_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_beginner_issues(languages: list, limit_per_lang: int = 3):
    """
    Fetch 'good first issue' issues for each language in the list.
    Returns combined list of unique issues (across languages).
    """
    all_issues = []
    
    for lang in languages:
        print(f"[GitHub] Fetching issues for language: {lang}")
        
        url = "https://api.github.com/search/issues"
        query = f'label:"good first issue" language:{lang} state:open is:issue'
        params = {
            "q": query,
            "per_page": limit_per_lang,
            "sort": "updated"
        }
        
        print(f"[GitHub] Query: {query}")
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print(f"[GitHub] Error for {lang}: {response.status_code}")
            continue
        
        data = response.json()
        items = data.get("items", [])
        print(f"[GitHub] Received {len(items)} issues for {lang}.")
        
        for issue in items:
            all_issues.append({
                "title": issue["title"],
                "url": issue["html_url"],
                "repo": issue["repository_url"].split("/repos/")[-1],
                "body_preview": (issue.get("body") or "")[:200],
                "number": issue["number"],
                "language": lang          # track which language
            })
    
    print(f"[GitHub] Total unique issues fetched: {len(all_issues)}")
    return all_issues


def get_repo_file_tree(repo_full_name: str, max_files: int = 100):
    """
    Fetch the top-level file tree of a repository.
    Returns a list of dicts with 'path', 'type' (file/dir), and 'url'.
    """
    print(f"[GitHub] Fetching file tree for {repo_full_name}...")
    
    # Use GitHub Contents API to get root directory
    url = f"https://api.github.com/repos/{repo_full_name}/contents"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"[GitHub] Error fetching tree: {response.status_code}")
        return []
    
    contents = response.json()
    # Build a simplified tree (only names and types)
    tree = []
    for item in contents[:max_files]:
        tree.append({
            "path": item["path"],
            "type": item["type"],   # "file" or "dir"
            "name": item["name"]
        })
    print(f"[GitHub] Retrieved {len(tree)} items from root.")
    return tree


def get_repo_contributing_guidelines(repo_full_name: str):
    """Fetch CONTRIBUTING.md file content if it exists."""
    url = f"https://api.github.com/repos/{repo_full_name}/contents/CONTRIBUTING.md"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[GitHub] No CONTRIBUTING.md found.")
        return None
    data = response.json()
    # Decode base64 content
    import base64
    content = base64.b64decode(data["content"]).decode("utf-8")
    print(f"[GitHub] Retrieved CONTRIBUTING.md ({len(content)} chars)")
    return content


def get_file_content(repo_full_name: str, file_path: str):
    """
    Fetch the raw content of a single file from GitHub.
    Returns the file content as string, or None if error.
    """
    print(f"[GitHub] Fetching file content: {file_path}")
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"[GitHub] Error fetching {file_path}: {response.status_code}")
        return None
    
    data = response.json()
    # Content is base64 encoded
    import base64
    content = base64.b64decode(data["content"]).decode("utf-8")
    print(f"[GitHub] Downloaded {len(content)} characters.")
    return content