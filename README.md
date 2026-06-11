# 🚀 FOSSFirst – Open Source Contribution Navigator

**FOSSFirst** is a **multi‑AI agent system** that helps students and beginners make their first open‑source contribution.  
It uses **LangGraph**, **Qwen Code 3B** (via Ollama), and the **GitHub API** to find beginner‑friendly issues, map the codebase, generate patches, run safe tests, and simulate a maintainer review – all **locally** and **without cloning** repositories.

> ✅ No paid APIs. ✅ No full repo clones. ✅ Complete privacy (runs on your machine).

---

## 🧠 Multi‑Agent Architecture

FOSSFirst orchestrates **4 specialized AI agents** (powered by Qwen) and **3 tool nodes** inside a LangGraph state machine.

| Agent | Role | Tools Used |
|-------|------|-------------|
| **Issue Ranker** | Scores issues (1–10 difficulty) and ranks them | Qwen Code 3B (Ollama) |
| **Codebase Mapper** | Analyzes repo file tree → suggests relevant files | GitHub API + Qwen |
| **Patch Writer** | Generates a unified diff (patch) to fix the issue | Qwen Code 3B |
| **Maintainer Simulator** | Reviews the patch against contributing guidelines | GitHub API + Qwen |

| Tool Node | Role |
|-----------|------|
| **GitHub Fetcher** | Searches for `good first issue` labels, fetches file trees, raw content, and `CONTRIBUTING.md` |
| **Sandbox Tester** | Validates patch format and (for Python) runs syntax checks |
| **Final Reporter** | Aggregates results and outputs a verdict |

---

## 🔁 Execution Flow (LangGraph)

```mermaid
graph TD
    Start([User: language]) --> A[Fetch Issues<br/>GitHub API]
    A --> B[Rank Issues<br/>Qwen Agent]
    B --> C{Human Selects Issue}
    C --> D[Get Repo Tree<br/>GitHub API]
    D --> E[Map Codebase<br/>Qwen Agent]
    E --> F[Fetch File Content<br/>GitHub API]
    F --> G[Write Patch<br/>Qwen Agent]
    G --> H[Test Patch<br/>Sandbox]
    H --> I{Tests passed?}
    I -->|No & retries left| G
    I -->|Yes| J[Fetch CONTRIBUTING.md<br/>GitHub API]
    J --> K[Simulate Maintainer<br/>Qwen Agent]
    K --> L[Generate Final Report]
    L --> End([Verdict: Ready / Needs revision])
💡 The graph includes conditional looping (up to 3 patch attempts) and a human‑in‑the‑loop interrupt for issue selection.

🛠️ Tech Stack
Orchestration: LangGraph (state machine + checkpointing)

LLM: Qwen Code 3B running locally via Ollama

APIs: GitHub REST API (free, 5000 req/hour with token)

Sandbox: Python subprocess + tempfile for safe patch testing

Language: Python 3.11+

📦 Installation
1. Clone the repository
bash
git clone https://github.com/your-username/FOSSFirst.git
cd FOSSFirst
2. Set up Python environment
bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
3. Install Ollama and pull Qwen model
bash
# Install Ollama from https://ollama.com/
ollama pull qwen2.5-coder:3b
4. Configure GitHub token
Create a .env file:

text
GITHUB_TOKEN=ghp_your_personal_access_token
Get a token from GitHub → Settings → Developer settings → Personal access tokens (classic).
Scopes needed: repo, public_repo.

🚀 Usage
bash
python main.py
The system will:

Fetch beginner‑friendly Python issues.

Rank them by difficulty.

Ask you to select one.

Analyze the repository, fetch relevant files, and generate a patch.

Test the patch in a sandbox.

Simulate a maintainer review.

Output a final report (ready to submit / needs revision).

Example output snippet
text
============================================================
FOSSFirst – FINAL CONTRIBUTION REPORT
============================================================
ISSUE:
  Title: Fix typo in error message
  Repo: pandas-dev/pandas
  ...
VERDICT: ✅ READY TO SUBMIT – The patch passes tests and maintainer approval.
============================================================
📁 Project Structure
text
FOSSFirst/
├── agents/               # 4 LLM‑based agents (ranker, mapper, writer, simulator)
├── tools/                # GitHub API, sandbox, helpers
├── ui/                   # CLI for human interrupt
├── state.py              # LangGraph state schema
├── graph.py              # Node/edge definition, conditional routing
├── main.py               # Entry point
├── final_report.py       # Aggregates state → human‑readable report
├── requirements.txt
└── .env                  # GitHub token (never committed)
Test scripts (test_phase*.py) are excluded from the final project.

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

Ollama and Qwen for local LLM

GitHub for their free API
