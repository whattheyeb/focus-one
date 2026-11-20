# focus-one

**English** | [한국어](README.ko.md)

A Claude Code plugin. While you wait for one answer, you write the next question in a memo pad instead of opening a new session right away.

- **⚡ Simple tasks**: work where you only need the result. Press ⏎ to open a new Claude Code session.
- **📘 Learning**: questions you want to understand. Press ⏎ to open a new session. If a learning session is already open, a warning appears first.

## Requirements

- Claude Code
- Python 3.8+ (standard library only, no pip install needed). The in-page session terminal bundles xterm.js 5.5.0 (MIT) in `app/vendor/`

## Install

```bash
claude plugin marketplace add whattheyeb/focus-one   # or a local path
claude plugin install focus-one@focus-one
```

Restart Claude Code after installing.

## Usage

| Action | How |
|---|---|
| Open the memo pad | `/focus-one` |
| Start only the server, no browser tab | `/focus-one server`. Use this when the memo pad lives inside Obsidian (Custom Frames or Web viewer at `http://127.0.0.1:47321/`) |
| Send | ⏎ button or `Ctrl/⌘ + Enter` |
| Log what you are doing right now (업무로그) | Type and press Enter. The time is stamped automatically and saved to `YYYY-MM-DD.md` (one file per day) in a single work log folder, shared by every memo pad tab whatever folder it was opened from. Entries go under a `## 업무로그` heading as `- [태그] 내용 [startTime:: HH:MM] [endTime:: HH:MM]`, so Obsidian Full Calendar can show them (Daily notes folder = the work log folder, format `YYYY-MM-DD`; Full Calendar source type "Daily Note", heading `업무로그`). Only today's entries are shown; "오늘 기록 복사" copies them as `- HH:MM~HH:MM [태그] 내용` |
| Tag a log entry | Pick a tag from the dropdown (AI/개발 · AI/개념공부/코드이해 · 코드 실행 · 질문 · 아이디어), or change it later with "수정". Entries left on "태그: 자동" are tagged every hour by `claude -p` (haiku); "지금 태그 붙이기" runs it right away |
| Ask about a part of an Obsidian note | Copy the text in Obsidian and paste it into a memo or a session tab. The server looks the text up in the Obsidian vaults listed in Obsidian's `obsidian.json` (recently opened notes first, markdown marks and spacing ignored) and, if a note contains it, adds `(출처: <note path>:<lines>)` on the next line. Text shorter than 10 characters, or not found in any note, is pasted as is |
| Change the folder new sessions open in | Edit the path at the top, then press Enter |
| Stop the server | The "종료" (stop) button at the top right, or `/focus-one stop` |

Set the work log folder in `~/.claude/focus-one/config.json` (read on every request, no restart needed), or override it with the `FOCUS_ONE_WORKLOG_DIR` environment variable. Default: `~/.claude/focus-one/worklog`.

```json
{ "worklog_dir": "C:\path\to\업무로그" }
```

Each sent note is saved to the following files.

```
~/.claude/focus-one/
├── simple.md       # simple-task log
├── learning.md     # learning log
└── history.jsonl   # the same log, machine-readable
```

## How new sessions open

| OS | Method |
|---|---|
| Windows | A tab inside the memo pad page, so it also works inside Obsidian. Each session runs in a pseudo console (ConPTY, Windows 10 1809+) owned by the server and is drawn with xterm.js. A learning question switches to its tab; a simple task opens its tab in the background. Shift+Enter adds a new line, Ctrl+C copies a selection (otherwise it interrupts), Ctrl+V pastes. Closing a running session's tab takes two clicks. Sessions end when the server stops. Set `FOCUS_ONE_TERMINAL=window` to get a separate console window per session instead |
| macOS | A new Terminal.app window |
| Linux | The first one found: gnome-terminal, konsole, xfce4-terminal, kitty, alacritty, wezterm, x-terminal-emulator, xterm. If none is found, the memo pad shows a command you can copy and run. |

## Security

The server listens only on `127.0.0.1:47321`. Every API request needs the random token embedded in the page, which stops other websites from opening sessions. Change the port with the `FOCUS_ONE_PORT` environment variable.
