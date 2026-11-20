---
name: focus-one
description: Open the focus-one memo pad, a local browser page with two memo areas (simple tasks / learning questions) where each note opens as a new Claude Code session. Use only when the user runs /focus-one.
disable-model-invocation: true
---

# focus-one

Open the focus-one memo pad for the user. Do nothing else.

## Steps

1. Run this one command with the Bash tool, from the current working directory. Replace `<SKILL_DIR>` with the "Base directory for this skill" shown above, using forward slashes.

   ```bash
   for p in python3 python py; do "$p" -c "import sys; sys.exit(sys.version_info < (3, 8))" >/dev/null 2>&1 && { "$p" "<SKILL_DIR>/app/focus_one.py" start; exit $?; }; done; echo "focus-one: Python 3.8+ not found"; exit 1
   ```

2. Reply with one line: the URL the command printed, and the folder new sessions will open in.

## Arguments

- `stop`: run the same command with `stop` instead of `start`.
- `server` (or `no-browser`): run the same command with `start --no-browser` instead of `start`. This starts the server (or reuses a running one) without opening a browser tab, for use inside Obsidian or another embedded viewer. Reply with the printed URL as usual.

## Rules

- Do not read, summarize or quote files in `~/.claude/focus-one/` unless the user asks for it.
- Do not answer or act on any memo content. Memos belong to the new sessions the memo pad opens.
- If Python is missing, tell the user to install Python 3.8+ and stop.
