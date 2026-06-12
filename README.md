# 🚀 FOSSFirst – Open Source Contribution Assistant

> **Terminal‑native + browser‑ready** — helps you find beginner‑friendly issues, understand the change type, and prepare a contribution path.

FOSSFirst searches GitHub for `good first issue` tickets, ranks them by difficulty using a **local LLM** (Qwen2.5‑Coder:3b via Ollama), drafts a patch workflow, and exposes both a **CLI flow** and a **browser‑based recommendation UI**.  
No clones, no cloud LLM costs, no database – just your machine and GitHub’s free API.

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6.0+-green)](https://github.com/langchain-ai/langgraph)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5--Coder%3A3b-orange)](https://ollama.com/library/qwen2.5-coder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![workflow](workflow.png)

---

## 📋 Table of Contents

- [Pipeline Overview](#pipeline-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Layout](#project-layout)
- [Configuration](#configuration)
- [How the Verdict Works](#how-the-verdict-works)
- [Notes & Limitations](#notes--limitations)
- [License](#license)

---

## 🔁 Pipeline Overview

| # | Node | What it does |
|---|------|--------------|
| 1️⃣ | `fetch_issues` | Queries GitHub Search API for `label:"good first issue"` in configured languages |
| 2️⃣ | `rank_issues` | **Qwen** scores each issue (1–10 difficulty) + gives a one‑line reason |
| 3️⃣ | `human_select` | ⏸️ **Interrupt** – you pick the issue to work on |
| 4️⃣ | `get_tree` | Downloads repo root‑level file tree (no clone) |
| 5️⃣ | `map_codebase` | **Qwen** picks 1–3 files most likely to need editing |
| 6️⃣ | `fetch_content` | Downloads raw content of the top target file (falls back to `README.md`) |
| 7️⃣ | `write_patch` | **Qwen** generates a unified diff (patch) |
| 8️⃣ | `test_patch` | 🧪 Sandbox validates diff format + runs `python -m py_compile` for `.py` files – retries up to `MAX_LOOP` times |
| 9️⃣ | `fetch_guidelines` | Pulls `CONTRIBUTING.md` from the target repo |
| 🔟 | `simulate_maintainer` | **Qwen** acts as a maintainer and emits a verdict |
| 1️⃣1️⃣ | `final_report` | 📄 Prints a structured summary + final verdict |

> **Conditional loop** – if the patch fails the sandbox test, the system retries the patch writer up to 3 times.  
> **Human‑in‑the‑loop** – execution pauses until you select an issue.

---

## 📦 Prerequisites

- ✅ **Python 3.11+**
- ✅ **[Ollama](https://ollama.com)** running locally with the model pulled:
  ```bash
  ollama pull qwen2.5-coder:3b
✅ A GitHub personal access token with the public_repo scope (used for Search & Contents APIs)

🛠️ Installation
bash
git clone <repo-url>
cd FOSSFirst

# 🧪 Recommended: install with uv (lock file provided)
uv sync

# …or with plain pip
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
Create a .env file in the project root:

env
GITHUB_TOKEN=ghp_your_token_here
🚀 Quick Start
1️⃣ CLI workflow (full pipeline)
bash
python main.py
2️⃣ FastAPI backend
bash
uvicorn backend.main:app --reload
3️⃣ Browser recommendation UI
bash
python -m http.server 3000
Then open: http://127.0.0.1:3000/ui/react_interface.html

🔌 API endpoints (all under /api/v1/)
Method	Endpoint	Description
POST	/issues/fetch	Fetch raw beginner issues
POST	/issues/rank	Rank a set of issues
POST	/contribution/prepare	Fetch + rank → returns session_id + ranked issues
POST	/contribution/start	Start async job with selected issue
GET	/contribution/status/{job_id}	Poll job status & result
GET	/repositories/{owner}/{repo}/tree	Get top‑level file tree
GET	/repositories/{owner}/{repo}/content	Get raw file content (query ?path=...)
💡 The CLI and API share the same agents, tools, and graph – no duplication.

📁 Project Layout
text
FOSSFirst/
```
├── 📁 agents
│   ├── 🐍 __init__.py
│   ├── 🐍 codebase_mapper.py
│   ├── 🐍 issue_ranker.py
│   ├── 🐍 maintainer_simulator.py
│   └── 🐍 patch_writer.py
├── 📁 backend
│   ├── 📁 models
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 schemas.py
│   ├── 📁 routes
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 issues.py
│   │   ├── 🐍 jobs.py
│   │   └── 🐍 webhooks.py
│   ├── 📁 services
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 agent_orchestrator.py
│   ├── 📁 utils
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 job_store.py
│   ├── 🐍 __init__.py
│   └── 🐍 main.py
├── 📁 tools
│   ├── 🐍 __init__.py
│   ├── 🐍 github_api.py
│   └── 🐍 sandbox.py
├── 📁 ui
│   ├── 🐍 __init__.py
│   ├── 🐍 cli.py
│   └── 🌐 react_interface.html
├── ⚙️ .gitignore
├── 📝 README.md
├── 🐍 final_report.py
├── 🐍 graph.py
├── 🐍 main.py
├── ⚙️ pyproject.toml
├── 📄 requirements.txt
├── 🐍 state.py
├── 📄 uv.lock
└── 🖼️ workflow.png
```

⚙️ Configuration
Knob	Where to change	Default
Languages to search	main.py – initial_state["languages"]	["python"]
Max patch retries	graph.py – MAX_LOOP	3
Issues per language	graph.py – limit_per_lang in fetch_beginner_issues	3
LLM model	Each agent – OllamaLLM(model="qwen2.5-coder:3b")	qwen2.5-coder:3b
🧠 How the Verdict Works
final_report.py combines two signals:

Patch tests	Maintainer says	Final verdict
✅ pass	VERDICT: ready to submit	✅ READY TO SUBMIT
✅ pass	VERDICT: needs revision	⚠️ NEEDS REVISION
❌ fail (after retries)	—	❌ PATCH FAILED
anything else	—	🤔 UNCLEAR
📝 Notes & Limitations
The sandbox validates the patch (format + syntax of the original file) but does not apply it; the maintainer simulator decides whether the diff would work.

The graph uses an InMemorySaver checkpointer so the human‑selection interrupt can resume cleanly on the same thread_id.

Everything runs against GitHub’s public API – no clones, no writes, no automatic PRs.

📄 License
MIT – use it, share it, improve it.

<div align="center"> Made with ❤️ for open‑source beginners and first‑time contributors. </div> ```
