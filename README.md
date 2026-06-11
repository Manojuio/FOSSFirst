# 🚀 FOSSFirst – Open Source Contribution Navigator

**FOSSFirst** is a **multi‑AI agent system** that helps students and beginners make their first open‑source contribution.  
It uses **LangGraph**, **Qwen2.5‑Coder:3b** (via Ollama), and the **GitHub API** to find beginner‑friendly issues, map the codebase, generate patches, run safe tests, and simulate a maintainer review – all **locally** and **without cloning** repositories.

> ✅ No paid APIs. ✅ No full repo clones. ✅ Complete privacy (runs on your machine).

---

## 🧠 Multi‑Agent Architecture

FOSSFirst orchestrates **4 specialized AI agents** (powered by Qwen2.5‑Coder) and **3 tool nodes** inside a LangGraph state machine.

| Agent | Role | Tools Used |
|-------|------|-------------|
| **Issue Ranker** | Scores issues (1–10 difficulty) and ranks them | Qwen2.5‑Coder (Ollama) |
| **Codebase Mapper** | Analyzes repo file tree → suggests relevant files | GitHub API + Qwen |
| **Patch Writer** | Generates a unified diff (patch) to fix the issue | Qwen2.5‑Coder |
| **Maintainer Simulator** | Reviews the patch against contributing guidelines | GitHub API + Qwen |

| Tool Node | Role |
|-----------|------|
| **GitHub Fetcher** | Searches for `good first issue` labels, fetches file trees, raw content, and `CONTRIBUTING.md` |
| **Sandbox Tester** | Validates patch format and (for Python) runs syntax checks |
| **Final Reporter** | Aggregates results and outputs a verdict |

---

## 🔁 Execution Flow (LangGraph)

The LangGraph state machine executes the following steps in order. The graph includes a conditional loop for patch testing and a human interrupt for issue selection.

Fetch Issues
→ Calls GitHub API to find good first issue tickets for the selected language.

Rank Issues
→ Uses Qwen2.5‑Coder:3b to assign a difficulty score (1–10) to each issue.

Human Select (interrupt)
→ Pauses execution and asks the user to pick one issue from the ranked list.

Get Repo Tree
→ Fetches the repository’s top‑level file tree (no cloning, just metadata).

Map Codebase
→ Qwen2.5‑Coder analyses the tree + issue → suggests 1‑3 relevant file paths.

Fetch File Content
→ Downloads the raw source code of the suggested files (only what is needed).

Write Patch
→ Qwen2.5‑Coder generates a unified diff (patch) to fix the issue.

Test Patch
→ Applies the patch in a temporary sandbox and runs a syntax/format check.

If the test passes → continue to step 9.

If the test fails → loop back to step 7 (up to 3 retries). After 3 failures, skip to step 11.

Fetch Contributing Guidelines
→ Retrieves CONTRIBUTING.md from the repository (if it exists).

Simulate Maintainer
→ Qwen2.5‑Coder reviews the patch against the issue + guidelines, producing structured feedback.

Generate Final Report
→ Aggregates all data and outputs a final verdict: Ready to submit / Needs revision / Uncertain.



---

## 🛠️ Tech Stack

- **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) (state machine + checkpointing)
- **LLM**: [Qwen2.5‑Coder:3b](https://ollama.com/library/qwen2.5-coder) running locally via [Ollama](https://ollama.com/)
- **APIs**: GitHub REST API (free, 5000 req/hour with token)
- **Sandbox**: Python `subprocess` + `tempfile` for safe patch testing
- **Language**: Python 3.11+

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/FOSSFirst.git
cd FOSSFirst
2. Set up Python environment
bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
3. Install Ollama and pull Qwen2.5‑Coder
bash
# Install Ollama from https://ollama.com/
ollama pull qwen2.5-coder:3b
4. Configure GitHub token
Create a .env file in the project root:

text
GITHUB_TOKEN=ghp_your_personal_access_token
Get a token from GitHub → Settings → Developer settings → Personal access tokens (classic).
Scopes needed: repo, public_repo.

🚀 Usage
bash
python main.py
The system will:

Fetch the 3 most recent good first issue issues for Python.

Rank them by difficulty using Qwen2.5‑Coder.

Ask you to select one.

Analyse the repository, fetch relevant files, and generate a patch.

Test the patch in a sandbox (format check + Python syntax).

Simulate a maintainer review using the project’s CONTRIBUTING.md (if present).

Output a final report with a clear verdict.

Example output (final report)
text
============================================================
FOSSFirst – FINAL CONTRIBUTION REPORT
============================================================
ISSUE:
  Title: Fix typo in error message
  Repo: pandas-dev/pandas
  URL: https://github.com/pandas-dev/pandas/issues/56789

PATCH:
  Length: 234 characters
  Preview:
--- a/pandas/core/frame.py
+++ b/pandas/core/frame.py
@@ -1234,7 +1234,7 @@
-    raise ValueError("recieved empty DataFrame")
+    raise ValueError("received empty DataFrame")

TESTS: PASSED
MAINTAINER REVIEW: Looks good, no missing tests.
VERDICT: ✅ READY TO SUBMIT
============================================================
📁 Project Structure (core files)
text
FOSSFirst/
├── agents/               # 4 LLM‑based agents (ranker, mapper, writer, simulator)
├── tools/                # GitHub API wrapper, sandbox, helpers
├── ui/                   # CLI for human interrupt
├── state.py              # LangGraph state schema (TypedDict)
├── graph.py              # Node/edge definitions + conditional routing
├── main.py               # Entry point
├── final_report.py       # Aggregates state → human‑readable report
├── requirements.txt
└── .env                  # GitHub token (gitignored)
Note: Test scripts (test_phase*.py) are not included in the final project.

🧪 Future Improvements
Recursive file tree (GitHub Git Trees API) for deeper codebase mapping

Support for JavaScript, Rust, and other languages

Real patch command integration + actual test suite execution

Web UI (React + FastAPI) to visualise agent workflow

Docker deployment

🤝 Contributing
We welcome contributions that improve the agent prompts, sandbox reliability, or language support.
Please open an issue or pull request.

📄 License
MIT – feel free to use, modify, and share.

🙏 Acknowledgements
LangGraph for agent orchestration

Ollama and Qwen2.5‑Coder for local LLM

GitHub for their free API
