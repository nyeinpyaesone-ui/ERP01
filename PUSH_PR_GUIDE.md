# Push & PR Merge Guide — qwen-code-8c721bc7 → main

Status: **local branch fully prepared, gates green; push blocked only by missing GitHub credentials in this sandbox.**

Verified facts (as of 2026-10-18):
- Local HEAD: `321cf52` on branch `qwen-code-8c721bc7-cf29-4740-b082-e667b12691b7`, working tree clean.
- Remote repo reachable anonymously: `https://github.com/nyeinpyaesone-ui/ERP01.git`
  - `origin/main` tip: `075558b` (Django-based ERP under `src/`)
  - Our branch descends from `9aa7b9b` (legacy scaffold) → **unrelated histories** vs current `main`.
- Dry-run merge simulation (`git merge-tree --allow-unrelated-histories`) shows **6 add/add conflicts**:
  `.gitignore`, `LICENSE`, `README.md`, `docs/README.md`, `requirements.txt`, `setup.cfg`
  (auto-merges cleanly for `config/__init__.py`; no other conflicts).

---

## Step 1 — Provide credentials (pick one)

```bash
# Option A: Personal Access Token (classic, scope: repo)
export GITHUB_TOKEN="ghp_xxx"          # or fine-grained PAT

# Option B: GitHub CLI
gh auth login
```

## Step 2 — Push the branch to origin

```bash
cd /workspace
git remote add origin https://github.com/nyeinpyaesone-ui/ERP01.git 2>/dev/null || true
git push -u origin qwen-code-8c721bc7-cf29-4740-b082-e667b12691b7
# HTTPS + token form:
# git push "https://x-access-token:${GITHUB_TOKEN}@github.com/nyeinpyaesone-ui/ERP01.git" \
#   qwen-code-8c721bc7-cf29-4740-b082-e667b12691b7
```

Pushing a new branch cannot conflict — it creates `refs/heads/qwen-code-8c721bc7-...` as-is.

## Step 3 — Open the PR

```bash
gh pr create \
  --base main \
  --head qwen-code-8c721bc7-cf29-4740-b082-e667b12691b7 \
  --title "chore: code-review remediation, cleanup, CI hardening (scaffold line)" \
  --body "$(cat <<'EOF'
Fixes from full code review: untracked .env, flake8/black configs, repaired scripts/new-feature.sh,
hermetic tests (58 passed, 90.5% coverage), production SECRET_KEY fail-fast guard, gitleaks CI step,
Actions bumped (checkout@v5/setup-python@v6/upload-artifact@v5), Python 3.12 alignment.

NOTE: This branch descends from legacy commit 9aa7b9b (flat scaffold); main has moved to the
Django layout under src/. Expect add/add conflicts in .gitignore, LICENSE, README.md,
docs/README.md, requirements.txt, setup.cfg — see resolution guide below.
EOF
)"
```

## Step 4 — Resolve the 6 known conflicts (recommended strategy)

Because `main` is now a Django project and our work targets the legacy flat scaffold, resolve with **main's side kept for app files**, ours merged in only where still relevant:

| File | Recommended resolution |
|---|---|
| `.gitignore` | Take **union**: main's entries + ours (`logs/`, `backups/`, `.coverage`, `coverage.xml`, `.env*` rules) |
| `LICENSE` | Keep whichever text is canonical (they differ only by holder/year formatting — verify, then pick one) |
| `README.md` | Keep **main's** (Django docs); port useful sections from ours (quality-gates, scripts usage) if desired |
| `docs/README.md` | Keep **main's**; append our maintenance notes if not duplicated |
| `requirements.txt` | Keep **main's** Django deps; add our dev tools lines (`black`, `flake8`, `pytest-cov`, pinned versions) if absent |
| `setup.cfg` | Merge: keep main's `[flake8]`/`[tool:pytest]` sections; ensure `max-line-length = 88`, `extend-ignore = E203,W503` |

Mechanics:

```bash
git checkout -b pr/qwen-merge origin/main
git merge --allow-unrelated-histories qwen-code-8c721bc7-cf29-4740-b082-e667b12691b7
# edit the 6 conflicted files per table above
git add -A && git commit        # completes merge
python -m pytest --cov --cov-fail-under=80   # re-verify after merge
black --check . && flake8 .
git push origin pr/qwen-merge
gh pr create --base main --head pr/qwen-merge ...
```

Alternative (cleaner long-term): open the PR against the still-existing legacy branch
`@ERP_v1.0.0` (tip `9aa7b9b`, direct ancestor of our branch → **zero conflicts**), and let the
Django `main` line evolve separately.

## Step 5 — Merge

```bash
gh pr checks <PR>            # wait for CI (gitleaks, black, flake8, pytest) green
gh pr merge <PR> --squash    # or --merge, per repo policy
```

Self-approval note: repo settings may require a second reviewer before merge is allowed.
