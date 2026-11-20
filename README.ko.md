# focus-one

[English](README.md) | **한국어**

Claude Code 플러그인입니다. 답변 하나를 기다리는 동안 떠오른 다음 질문을 바로 새 세션으로 열지 않고 메모장에 적어 둡니다.

- **⚡ 단순 작업**: 결과만 있으면 되는 일. ⏎를 누르면 새 Claude Code 세션이 열립니다.
- **📘 학습**: 이해하고 싶은 질문. ⏎를 누르면 새 세션이 열립니다. 학습 세션이 이미 열려 있으면 먼저 경고가 뜹니다.

## 요구 사항

- Claude Code
- Python 3.8 이상 (표준 라이브러리만 쓰므로 pip install이 필요 없습니다). 페이지 안의 세션 터미널은 `app/vendor/`에 들어 있는 xterm.js 5.5.0(MIT)으로 그립니다.

## 설치

```bash
claude plugin marketplace add whattheyeb/focus-one   # 로컬 경로도 됩니다
claude plugin install focus-one@focus-one
```

설치한 뒤 Claude Code를 다시 시작합니다.

## 사용법

| 하고 싶은 일 | 방법 |
|---|---|
| 메모장 열기 | `/focus-one` |
| 브라우저 탭 없이 서버만 켜기 | `/focus-one server`. 메모장을 Obsidian 안에 띄울 때 씁니다 (Custom Frames나 Web viewer에서 `http://127.0.0.1:47321/` 열기) |
| 보내기 | ⏎ 버튼 또는 `Ctrl/⌘ + Enter` |
| 지금 하는 일 기록하기 (업무로그) | 입력하고 Enter를 누릅니다. 시각이 자동으로 찍히고, 업무로그 폴더 하나에 하루 한 파일(`YYYY-MM-DD.md`)로 저장됩니다. 어느 폴더에서 연 메모장 탭이든 같은 폴더를 씁니다. 기록은 `## 업무로그` 제목 아래에 `- [태그] 내용 [startTime:: HH:MM] [endTime:: HH:MM]` 형식으로 들어가므로 Obsidian Full Calendar에서 볼 수 있습니다 (Daily notes 폴더 = 업무로그 폴더, 형식 `YYYY-MM-DD`; Full Calendar 소스 종류 "Daily Note", 제목 `업무로그`). 화면에는 오늘 기록만 보이고, "오늘 기록 복사"를 누르면 `- HH:MM~HH:MM [태그] 내용` 형식으로 복사됩니다 |
| 기록에 태그 달기 | 드롭다운에서 태그(AI/개발 · AI/개념공부/코드이해 · 코드 실행 · 질문 · 아이디어)를 고르거나, 나중에 "수정"으로 바꿉니다. "태그: 자동"으로 둔 기록은 `claude -p`(haiku)가 한 시간마다 태그를 붙입니다. "지금 태그 붙이기"를 누르면 바로 붙입니다 |
| Obsidian 노트 일부를 두고 질문하기 | Obsidian에서 텍스트를 복사해 메모나 세션 탭에 붙여 넣습니다. 서버가 Obsidian의 `obsidian.json`에 등록된 vault에서 그 텍스트를 찾고(최근 연 노트부터, 마크다운 기호와 공백은 무시), 찾으면 다음 줄에 `(출처: <노트 경로>:<줄 번호>)`를 붙입니다. 10자보다 짧거나 어느 노트에도 없는 텍스트는 그대로 붙여 넣습니다 |
| 새 세션이 열릴 폴더 바꾸기 | 맨 위의 경로를 고치고 Enter를 누릅니다 |
| 서버 끄기 | 오른쪽 위 "종료" 버튼 또는 `/focus-one stop` |

업무로그 폴더는 `~/.claude/focus-one/config.json`에서 정합니다. 서버가 요청마다 이 파일을 다시 읽으므로 재시작할 필요가 없습니다. `FOCUS_ONE_WORKLOG_DIR` 환경 변수를 설정하면 config.json 값 대신 환경 변수 값을 씁니다. 기본값은 `~/.claude/focus-one/worklog`입니다.

```json
{ "worklog_dir": "C:\path\to\업무로그" }
```

보낸 메모는 아래 파일에 저장됩니다.

```
~/.claude/focus-one/
├── simple.md       # 단순 작업 기록
├── learning.md     # 학습 기록
└── history.jsonl   # 같은 기록을 프로그램이 읽기 쉬운 형식으로
```

## 새 세션이 열리는 방식

| OS | 방식 |
|---|---|
| Windows | 메모장 페이지 안의 탭으로 열립니다. 그래서 Obsidian 안에서도 됩니다. 서버가 세션마다 의사 콘솔(ConPTY, Windows 10 1809 이상)을 띄우고 xterm.js로 화면에 그립니다. 학습 질문을 보내면 그 탭으로 넘어가고, 단순 작업은 탭을 뒤에서 엽니다. Shift+Enter는 줄바꿈, Ctrl+C는 선택한 텍스트가 있으면 복사하고 없으면 실행을 중단합니다. Ctrl+V는 붙여넣기입니다. 실행 중인 세션의 탭은 두 번 눌러야 닫힙니다. 서버를 끄면 세션도 끝납니다. 세션마다 별도 콘솔 창을 띄우려면 `FOCUS_ONE_TERMINAL=window`를 설정합니다 |
| macOS | 새 Terminal.app 창 |
| Linux | gnome-terminal, konsole, xfce4-terminal, kitty, alacritty, wezterm, x-terminal-emulator, xterm 순서로 찾아서 처음 찾은 터미널을 씁니다. 하나도 없으면 메모장이 복사해서 실행할 명령을 보여 줍니다 |

## 보안

서버는 `127.0.0.1:47321`에서만 요청을 받습니다. 모든 API 요청에는 페이지에 들어 있는 무작위 토큰이 있어야 하므로, 다른 웹사이트가 세션을 열 수 없습니다. 포트는 `FOCUS_ONE_PORT` 환경 변수로 바꿉니다.
