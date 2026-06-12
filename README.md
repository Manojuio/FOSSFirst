# FOSSFirst

> A terminal-native open-source contribution assistant that helps you find beginner-friendly issues, understand the likely change type, and prepare a contribution path from the browser.

FOSSFirst searches GitHub for `good first issue` tickets, ranks them by difficulty using a local LLM model via Ollama, drafts a patch workflow, and exposes both a CLI flow and a browser-based recommendation UI for exploring issues before you start coding.

This repository is ready to push to GitHub on the `main` branch after installing dependencies and setting your local environment variables.

![workflow](workflow.png)

---

## Pipeline

| # | Node | What it does |
|---|------|--------------|
| 1 | `fetch_issues` | Queries the GitHub Search API for `label:"good first issue"` issues in the configured languages |
| 2 | `rank_issues` | Qwen scores each issue on a 1–10 difficulty scale and gives a one-line reason |
| 3 | `human_select` | **Interrupt** — you pick the issue to work on |
| 4 | `get_tree` | Downloads the repo's root-level file tree |
| 5 | `map_codebase` | Qwen picks the 1–3 files most likely to need editing |
| 6 | `fetch_content` | Downloads the raw content of the top target file (falls back to `README.md`) |
| 7 | `write_patch` | Qwen generates a unified diff |
| 8 | `test_patch` | Sandbox validates diff format and runs `python -m py_compile` for `.py` files; retries up to `MAX_LOOP` times |
| 9 | `fetch_guidelines` | Pulls `CONTRIBUTING.md` from the target repo |
| 10 | `simulate_maintainer` | Qwen plays the role of a maintainer and emits a verdict |
| 11 | `final_report` | Prints a structured summary |

---

## Prerequisites

- **Python 3.11+**
- **[Ollama](https://ollama.com)** running locally with the model pulled:
  ```bash
  ollama pull qwen2.5-coder:3b
  ```
- A **[GitHub personal access token](https://github.com/settings/tokens)** with the `public_repo` scope (used for the Search & Contents APIs)

---

## Installation

```bash
git clone <repo-url>
cd FOSSFirst

# (Recommended) install with uv — a uv.lock is checked in
uv sync

# …or with plain pip
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=ghp_your_token_here
```

---

## Quick start

### 1) Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS / Linux
pip install -r requirements.txt
```

### 2) Configure the environment

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_token_here
```

### 3) Run the CLI workflow

```bash
python main.py
```

### 4) Run the backend API

```bash
uvicorn backend.main:app --reload
```

### 5) Open the React recommendation UI

Serve the UI from the repository root:

```bash
python -m http.server 3000
```

Then open:

- http://127.0.0.1:3000/ui/react_interface.html

### FastAPI backend

The project also exposes the same workflow as a REST API without changing the CLI:

```bash
uvicorn backend.main:app --reload
```

Useful API endpoints:

- POST /api/v1/issues/fetch
- POST /api/v1/issues/rank
- POST /api/v1/contribution/prepare
- POST /api/v1/contribution/start
- GET /api/v1/contribution/status/{job_id}
- GET /api/v1/repositories/{owner}/{repo}/tree
- GET /api/v1/repositories/{owner}/{repo}/content

The browser UI uses the same live issue fetch + ranking flow from the FastAPI backend and presents issue recommendations with difficulty labels and GitHub links. The CLI path still runs the full graph-based workflow for patch generation and review.

---

## Project layout

```
FOSSFirst/
├── main.py                      # entry point — builds the graph and invokes it
├── state.py                     # TypedDict describing the shared graph state
├── graph.py                     # LangGraph workflow + node functions
├── final_report.py              # report formatter
├── agents/
│   ├── issue_ranker.py          # LLM difficulty scoring
│   ├── codebase_mapper.py       # LLM file-tree → target paths
│   ├── patch_writer.py          # LLM unified-diff generator
│   └── maintainer_simulator.py  # LLM review against CONTRIBUTING.md
├── tools/
│   ├── github_api.py            # Search + Contents API client
│   ├── sandbox.py               # patch format check + py_compile
│   └── ollama_client.py         # shared LLM client (reserved)
├── ui/
│   ├── react_interface.html     # browser recommendation UI
│   └── cli.py                   # interactive issue picker
├── workflow.png                 # pipeline diagram
├── requirements.txt
└── pyproject.toml
```

---

## Configuration

A few knobs you can tweak:

- **Languages to search** — edit the `languages` list in `main.py`:
  ```python
  initial_state: State = {
      "languages": ["python", "javascript", "rust"],
      ...
  }
  ```
- **Max patch retries** — change `MAX_LOOP` in `graph.py` (default `3`).
- **Issues per language** — `limit_per_lang` argument to `fetch_beginner_issues` in `graph.py` (default `3`).
- **LLM model** — every agent instantiates `OllamaLLM(model="qwen2.5-coder:3b")`; swap the model name to experiment.

---

## How the verdict is decided

`final_report.py` looks at two signals:

| Patch tests | Maintainer says | Final verdict |
|---|---|---|
| ✅ pass | `VERDICT: ready to submit` | ✅ READY TO SUBMIT |
| ✅ pass | `VERDICT: needs revision` | ⚠️ NEEDS REVISION |
| ❌ fail (after retries) | — | ❌ PATCH FAILED |
| anything else | — | 🤔 UNCLEAR |

---

## Notes & limitations

- The sandbox **validates** the patch (format + syntax of the original file) but does not actually apply it; the simulated maintainer step is what decides whether the diff "would" work.
- The graph uses an `InMemorySaver` checkpointer so the human-selection interrupt can resume cleanly on the same `thread_id`.
- Everything runs against GitHub's **public** API surface; no clones, no writes, no PRs are opened by FOSSFirst itself.

---

## License

MIT
