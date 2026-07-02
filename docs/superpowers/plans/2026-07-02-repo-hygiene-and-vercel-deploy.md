# Repo Hygiene & Backend Vercel Deployment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the `.gitignore` bug that has been silently dropping the Flutter mobile source from every commit, and get the existing FastAPI backend live on Vercel with real Groq providers — producing a stable, publicly reachable API URL that later plans (mobile rebuild, new features) build against.

**Architecture:** No application architecture changes. This plan is pure repo hygiene + deployment configuration: scoped `.gitignore` files, a `[tool.vercel]` entrypoint pointing at the existing `app.main:app`, a `requirements.txt` mirroring `pyproject.toml`, and CORS middleware. The FastAPI app, provider pattern, and `/conversation` endpoint are untouched.

**Tech Stack:** FastAPI (existing), Vercel Python runtime (Fluid Compute), Vercel CLI, pytest.

## Global Constraints

- Python `>=3.11` (from `backend/pyproject.toml`); pin Vercel's `.python-version` to `3.13` (matches locally installed interpreter and is a currently supported Vercel Python version).
- `GROQ_API_KEY` and `GROQ_MULTIMODAL_MODEL` are required whenever `USE_REAL_PROVIDERS=true` (enforced today in `backend/app/main.py:19-21`) — never hardcode these values in any file; they are supplied as Vercel environment variables by the human operator.
- One commit per logical file change (per repo convention) with descriptive messages; no destructive git operations without explicit confirmation.
- Every code change ships with a passing test before commit (TDD).
- Never write secrets (API keys) into shell commands, files, or commit messages.

---

## Task 1: Split the root `.gitignore` and add a scoped `backend/.gitignore`

**Files:**
- Modify: `.gitignore` (root)
- Create: `backend/.gitignore`
- Verify via: `git check-ignore` (no pytest applicable — this is a config-only task)

**Interfaces:**
- Consumes: nothing from prior tasks.
- Produces: a repo state where `mobile/lib/**` is trackable by git. Later mobile-rebuild plans depend on this.

**Context:** The current root `.gitignore` is a full Python project template. Its line 17 (`lib/`) — meant to ignore Python's `lib/` build directory — also matches Flutter's `mobile/lib/` **source root**, since git patterns without a leading `/` match at any depth. Every historical commit to `mobile/` has silently excluded the actual app code; only `mobile/test/` (which doesn't match any ignore pattern) survived.

- [ ] **Step 1: Reproduce the bug (confirm before fixing)**

Run:
```bash
mkdir -p mobile/lib/features/conversation
touch mobile/lib/main.dart
git check-ignore -v mobile/lib/main.dart
```
Expected output (confirms the bug):
```
.gitignore:17:lib/	mobile/lib/main.dart
```

- [ ] **Step 2: Replace the root `.gitignore` with a minimal, cross-cutting-only file**

Replace the full contents of `.gitignore` (root) with:

```gitignore
# OS
.DS_Store
Thumbs.db

# Editors
.vscode/
.idea/

# Environment secrets (checked at repo root by backend/app/core/config.py)
.env
.env.local

# Vercel CLI local state
.vercel
```

- [ ] **Step 3: Create `backend/.gitignore` with the Python-specific patterns moved from root**

Create `backend/.gitignore`:

```gitignore
# Byte-compiled / optimized files
__pycache__/
*.py[codz]
*$py.class

# Distribution / packaging
.Python
build/
dist/
*.egg-info/
MANIFEST

# Test / coverage
.pytest_cache/
.coverage
.coverage.*
htmlcov/
cover/

# Type checkers / linters
.mypy_cache/
.ruff_cache/

# Environments
.venv
venv/
env/

# Env files (also checked here since backend/ is the Vercel project root)
.env
.env.local

# Logs
*.log

# Vercel CLI local state
.vercel
```

- [ ] **Step 4: Verify the bug is fixed**

Run:
```bash
git check-ignore -v mobile/lib/main.dart || echo "NOT IGNORED — fixed"
git check-ignore -v backend/__pycache__/x.pyc
```
Expected:
- First command prints `NOT IGNORED — fixed` (no match found, `git check-ignore` exits 1).
- Second command matches `backend/.gitignore:2:__pycache__/`.

- [ ] **Step 5: Clean up the reproduction artifacts and stage real changes**

Run:
```bash
rm -rf mobile/lib
git add .gitignore backend/.gitignore
git status
```
Expected: `.gitignore` shows as modified, `backend/.gitignore` shows as a new file, no `mobile/` changes staged.

- [ ] **Step 6: Commit**

```bash
git commit -m "$(cat <<'EOF'
fix(gitignore): scope Python ignores to backend/, unblock mobile/lib/

Root .gitignore was a Python template whose lib/ pattern silently
ignored the entire Flutter mobile/lib/ source tree. Every historical
mobile commit excluded the actual app code, leaving only mobile/test/
tracked. Split into a minimal root .gitignore and a Python-specific
backend/.gitignore so mobile/lib/ is trackable going forward.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Record decision D-014 in `docs/DECISIONS.md`

**Files:**
- Modify: `docs/DECISIONS.md`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing consumed by later tasks (documentation only).

- [ ] **Step 1: Append the decision record**

Add to the end of `docs/DECISIONS.md`:

```markdown

---

## D-014: Scoped `.gitignore` Files Per Language Root

**Decision**

Use a minimal root `.gitignore` for cross-cutting, OS/editor/secret patterns only. Each
language root (`backend/`, `mobile/`) owns a `.gitignore` scoped to its own toolchain.

**Reason**

The original root `.gitignore` was a Python template. Its `lib/` pattern silently matched
Flutter's `mobile/lib/` source root, causing every historical mobile commit to exclude the
actual app code. A single shared ignore file across a polyglot monorepo is a recurring
footgun; scoping ignore files to their language root prevents one toolchain's conventions
from silently deleting another's source tree.
```

- [ ] **Step 2: Verify**

Run:
```bash
grep -n "D-014" docs/DECISIONS.md
```
Expected: one match showing the new heading.

- [ ] **Step 3: Commit**

```bash
git add docs/DECISIONS.md
git commit -m "$(cat <<'EOF'
docs: record D-014 scoped gitignore decision

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Add CORS middleware to the FastAPI app

**Files:**
- Modify: `backend/app/main.py`
- Test: `backend/tests/unit/test_main.py` (new file — `app/main.py` has no dedicated test file yet)

**Interfaces:**
- Consumes: `app.main.create_app()` (existing, unchanged signature).
- Produces: `app.main.app` now includes `CORSMiddleware` in `app.user_middleware`. Later plans (mobile web/dev testing) rely on this being present.

**Context:** Vercel-hosted APIs are reachable from browsers (web dev testing, future admin tooling). The API has no authentication or cookies, so an open CORS policy carries no session-hijack risk today; this should be revisited if auth is ever added.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/unit/test_main.py`:

```python
from __future__ import annotations

from starlette.middleware.cors import CORSMiddleware

from app.main import create_app


def test_app_has_cors_middleware_allowing_all_origins() -> None:
    app = create_app()

    cors_entries = [m for m in app.user_middleware if m.cls is CORSMiddleware]

    assert len(cors_entries) == 1
    assert cors_entries[0].kwargs["allow_origins"] == ["*"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_main.py -v`
Expected: FAIL — `assert len(cors_entries) == 1` fails with `0 == 1` (no CORS middleware registered yet).

- [ ] **Step 3: Add CORS middleware in `app/main.py`**

In `backend/app/main.py`, add the import at the top (after the existing `from fastapi import FastAPI` line):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
```

Then, immediately after `app = FastAPI(title=settings.app_name, debug=settings.debug)` (currently line 42), insert:

```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

The full modified block (`backend/app/main.py` around lines 42-44) should read:

```python
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(create_conversation_router(service))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_main.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full backend test suite to confirm no regressions**

Run: `cd backend && python3 -m pytest -v`
Expected: all tests pass (existing suite + the new `test_main.py`).

- [ ] **Step 6: Commit**

```bash
git add backend/app/main.py backend/tests/unit/test_main.py
git commit -m "$(cat <<'EOF'
feat(backend): add permissive CORS middleware

Enables browser-based dev/web testing against the API. No auth or
cookies exist yet, so an open origin policy carries no session risk;
revisit if authentication is added later.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Configure the Vercel Python entrypoint

**Files:**
- Modify: `backend/pyproject.toml`
- Create: `backend/requirements.txt`
- Create: `backend/.python-version`
- Create: `backend/vercel.json`
- Modify: `docs/DECISIONS.md`

**Interfaces:**
- Consumes: `app.main:app` (existing FastAPI instance, unchanged).
- Produces: a Vercel-deployable `backend/` directory. Task 5 (local `vercel dev` verification) and Task 6 (production deploy) depend on this.

**Context (from Vercel's FastAPI framework docs):** Vercel's Python runtime detects a FastAPI app via `[tool.vercel] entrypoint = "<module>:<attr>"` in `pyproject.toml` — no wrapper file needs to be created, and `app/main.py` does not need to move. Vercel's Python builder requires a `requirements.txt` (it does not read `pyproject.toml` dependencies directly), and `.python-version` pins the interpreter version.

- [ ] **Step 1: Add the Vercel entrypoint to `pyproject.toml`**

Append to `backend/pyproject.toml`:

```toml

[tool.vercel]
entrypoint = "app.main:app"
```

- [ ] **Step 2: Create `backend/requirements.txt` mirroring installed dependency versions**

Create `backend/requirements.txt`:

```text
fastapi==0.136.1
groq==1.4.0
pydantic==2.12.5
pillow==12.0.0
uvicorn==0.47.0
```

- [ ] **Step 3: Pin the Python version**

Create `backend/.python-version`:

```text
3.13
```

- [ ] **Step 4: Create `backend/vercel.json`**

Create `backend/vercel.json`:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "fastapi",
  "functions": {
    "app/main.py": {
      "maxDuration": 60
    }
  }
}
```

`maxDuration: 60` covers the ASR → Vision → OCR → LLM → TTS chain on a Hobby-tier project; raise it in this file if the account is on a Pro plan and latency testing shows it's needed.

- [ ] **Step 5: Verify locally that the app still imports and runs standalone (sanity check, not yet via Vercel)**

Run:
```bash
cd backend && python3 -m pytest -v
```
Expected: full suite still passes — these are config/manifest files only, no Python source changed.

- [ ] **Step 6: Commit the Vercel entrypoint configuration**

```bash
git add backend/pyproject.toml backend/requirements.txt backend/.python-version backend/vercel.json
git commit -m "$(cat <<'EOF'
build(backend): configure Vercel Python entrypoint

Points Vercel's FastAPI framework detection at the existing
app.main:app via [tool.vercel] entrypoint, so no wrapper file or
directory restructuring is needed. Adds requirements.txt (Vercel's
Python builder does not read pyproject.toml dependencies directly)
and pins the interpreter to 3.13 via .python-version.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 7: Record decision D-016 in `docs/DECISIONS.md`**

Add to the end of `docs/DECISIONS.md`:

```markdown

---

## D-016: Deploy the Backend on Vercel via `[tool.vercel]` Entrypoint

**Decision**

Deploy the FastAPI backend on Vercel's Python runtime (Fluid Compute). Point Vercel at the
existing `app.main:app` instance through `[tool.vercel] entrypoint` in `pyproject.toml`
rather than creating a wrapper file or moving the app under an `api/` directory.

**Reason**

Vercel's FastAPI framework detection supports a configurable entrypoint, so the existing
package layout (`app/main.py`, `app/api/`, `app/services/`, `app/providers/`) stays
untouched. Fluid Compute's 300s ceiling comfortably covers the ASR → Vision → OCR → LLM →
TTS chain, and Vercel's Git-integration deploys give preview URLs on every PR for free.
```

- [ ] **Step 8: Verify**

Run:
```bash
grep -n "D-016" docs/DECISIONS.md
```
Expected: one match showing the new heading.

- [ ] **Step 9: Commit the decision record**

```bash
git add docs/DECISIONS.md
git commit -m "$(cat <<'EOF'
docs: record D-016 Vercel deployment decision

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Link the Vercel project and verify locally with `vercel dev`

**Files:** none (CLI/account setup only — no repo changes in this task).

**Interfaces:**
- Consumes: `backend/vercel.json`, `backend/pyproject.toml` (Task 4).
- Produces: a linked Vercel project (`backend/.vercel/project.json`, gitignored) and confirmation the app runs correctly under Vercel's local emulator before touching production.

> **Human action required:** this task needs an interactive terminal and a Vercel account login. It cannot be run unattended by an agent.

- [ ] **Step 1: Log in to Vercel CLI (if not already)**

Run:
```bash
vercel login
```
Follow the interactive prompt (email or GitHub OAuth).

- [ ] **Step 2: Link the `backend/` directory as its own Vercel project**

Run from inside `backend/`:
```bash
cd backend && vercel link
```
When prompted:
- "Set up ...?" → yes
- "Which scope?" → your account/team
- "Link to existing project?" → no (first time)
- "What's your project's name?" → `be-my-eye-backend` (or accept default)
- "In which directory is your code located?" → `./` (already inside `backend/`)

Expected: CLI reports the project is linked and creates `backend/.vercel/` (already covered by `backend/.gitignore`'s `.vercel` entry from Task 1).

- [ ] **Step 3: Run the app under Vercel's local dev emulator**

Run:
```bash
cd backend && vercel dev
```
Expected: CLI starts a local server (typically `http://localhost:3000`) that routes through Vercel's Python runtime emulation.

- [ ] **Step 4: Smoke-test the health endpoint through the emulator**

In a second terminal:
```bash
curl -s http://localhost:3000/health
```
Expected: `{"status":"ok"}` — confirms Vercel's Python runtime can load `app.main:app` via the configured entrypoint. (`USE_REAL_PROVIDERS` defaults to `false` locally since no env vars are set yet, so `/conversation` will use fake providers if exercised — that's expected at this stage.)

- [ ] **Step 5: Stop the dev server**

Stop the `vercel dev` process (Ctrl+C in its terminal).

No commit for this task — it's verification only, no files changed beyond the gitignored `.vercel/` directory.

---

## Task 6: Provision production environment variables and deploy

**Files:** none (Vercel project configuration + deploy only).

**Interfaces:**
- Consumes: the linked Vercel project from Task 5.
- Produces: a live production URL serving `/health` and `/conversation` with real Groq providers. This URL is the value later plans (mobile rebuild) configure as `BACKEND_URL`.

> **Human action required throughout:** API key entry and the go/no-go to deploy to production must be done by a human, not an agent — never pipe a secret value through an agent-run shell command.

- [ ] **Step 1: Gather required values before starting**

You will need, from https://console.groq.com/keys and https://console.groq.com/docs/models:
- `GROQ_API_KEY` — your Groq API key.
- `GROQ_MULTIMODAL_MODEL` — a Groq-hosted vision-capable model ID from your account's available models (required; the app raises `RuntimeError` at startup without it — see `backend/app/main.py:19-21`).
- Optionally override: `GROQ_LLM_MODEL` (default `llama-3.3-70b-versatile`), `GROQ_ASR_MODEL` (default `whisper-large-v3`), `GROQ_TTS_MODEL` (default `canopylabs/orpheus-arabic-saudi`), `GROQ_TTS_VOICE` (default `abdullah`), `GROQ_ASR_LANGUAGE` (default `ar`) — see `backend/app/core/config.py:29-41`. Leave these unset to keep the current Arabic-language defaults.

- [ ] **Step 2: Add each environment variable to the Production environment**

Run each of these from `backend/` and paste the value when prompted (values are entered interactively, not passed as CLI arguments, so they never appear in shell history):

```bash
vercel env add USE_REAL_PROVIDERS production
```
Enter: `true`

```bash
vercel env add GROQ_API_KEY production
```
Enter your Groq API key.

```bash
vercel env add GROQ_MULTIMODAL_MODEL production
```
Enter your chosen multimodal model ID.

- [ ] **Step 3: Verify the variables are registered**

Run:
```bash
vercel env ls production
```
Expected: `USE_REAL_PROVIDERS`, `GROQ_API_KEY`, `GROQ_MULTIMODAL_MODEL` listed (values shown as encrypted/hidden).

- [ ] **Step 4: Deploy to production**

Run:
```bash
cd backend && vercel deploy --prod
```
Expected: CLI prints a build log and, on success, a production URL (for example `https://be-my-eye-backend.vercel.app`). Note this URL — it is needed by every later plan.

- [ ] **Step 5: Verify the live health endpoint**

Run (replace with your actual production URL):
```bash
curl -s https://<your-production-url>/health
```
Expected: `{"status":"ok"}`.

- [ ] **Step 6: Verify the live `/conversation` endpoint with real providers**

Run:
```bash
curl -s -X POST https://<your-production-url>/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "deploy-smoke-test",
    "image_base64": "'"$(python3 -c "
import base64, io
from PIL import Image
buf = io.BytesIO()
Image.new('RGB', (32, 32), color='white').save(buf, format='PNG')
print(base64.b64encode(buf.getvalue()).decode())
")"'",
    "audio_base64": "'"$(python3 -c "
import base64, io, wave
buf = io.BytesIO()
with wave.open(buf, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(b'\x00\x00' * 1600)
print(base64.b64encode(buf.getvalue()).decode())
")"'",
    "debug": true
  }'
```
Expected: HTTP 200 with a JSON body containing non-empty `text` and `audio_base64` fields, and a `debug` object showing which providers were selected. (A blank/silent audio clip may transcribe to empty or noisy text — the goal here is confirming the full pipeline executes end-to-end without error, not response quality.)

- [ ] **Step 7: Record the live URL in `docs/ROADMAP.md`**

This is completed together with Task 7 below.

No code commit for this task (environment variables and deploys are Vercel project state, not repo state).

---

## Task 7: Update `docs/ROADMAP.md` status

**Files:**
- Modify: `docs/ROADMAP.md`

**Interfaces:**
- Consumes: the production URL obtained in Task 6, Step 4.
- Produces: nothing consumed by later tasks (documentation only).

- [ ] **Step 1: Update the progress tracker table**

In `docs/ROADMAP.md`, find the `## Progress Tracker` table (currently around line 168) and update the `Backend foundation` row's Notes cell to append: `Deployed to Vercel at <your-production-url>.`

- [ ] **Step 2: Update "Not Done Yet" / "In Progress" sections**

Under `## Current Status`, move "Backend deployed to Vercel with real providers" from an implicit gap into the `### Done` list (as a new numbered item at the end), since this plan completes it.

- [ ] **Step 3: Verify**

Run:
```bash
grep -n "Vercel" docs/ROADMAP.md
```
Expected: at least two matches (the new Done item and the updated table row).

- [ ] **Step 4: Commit**

```bash
git add docs/ROADMAP.md
git commit -m "$(cat <<'EOF'
docs: mark backend Vercel deployment done in roadmap

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Definition of Done

- [ ] `git check-ignore -v mobile/lib/main.dart` reports no match.
- [ ] `cd backend && python3 -m pytest -v` passes in full, including the new `test_main.py`.
- [ ] `backend/vercel.json`, `backend/requirements.txt`, `backend/.python-version`, and the `[tool.vercel]` entry in `backend/pyproject.toml` exist.
- [ ] `curl https://<production-url>/health` returns `{"status":"ok"}` from the live Vercel deployment.
- [ ] `curl -X POST https://<production-url>/conversation` (real providers) returns HTTP 200 with non-empty `text` and `audio_base64`.
- [ ] `docs/DECISIONS.md` contains D-014; `docs/ROADMAP.md` reflects the deployed status.
- [ ] Every task above is committed as its own commit (no bundled multi-concern commits).
