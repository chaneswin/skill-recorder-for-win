# Skill Recorder for Windows

操作錄一遍，AI 幫你做千遍。

Skill Recorder for Windows 可以錄製你的滑鼠點擊、鍵盤輸入與螢幕截圖，並匯出成結構化 Markdown。把錄製結果交給 Claude、ChatGPT、Codex 等 AI，AI 就能理解你的操作流程，接著協助寫程式、整理操作規則或製作可重複使用的 Skill。

本專案是 [GrapeBear/skill-recorder](https://github.com/GrapeBear/skill-recorder) 的 Windows 移植版。保留原專案「真人示範一次，讓 AI 理解流程」的核心概念與模組劃分，並將 macOS 專用的事件監聽與視窗介面改寫為 Windows 實作。

這個工具負責「錄製流程並交給 AI 理解」，本身不會回放操作，也不是 RPA 執行器。

## 工作原理

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   使用者操作  │────▶│   Windows    │────▶│  Markdown   │
│   電腦流程    │     │    錄製器     │     │  內嵌截圖    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │ 交給 AI
                                                 ▼
                                          ┌─────────────┐
                                          │     AI      │
                                          │  理解操作流程 │
                                          │  產生 Skill  │
                                          └─────────────┘
```

## 功能特色

- **Windows 原生控制視窗** — 開始錄製、停止匯出與開啟結果資料夾
- **全域操作記錄** — 捕捉滑鼠點擊、滾動與鍵盤輸入
- **智慧截圖** — 每次點擊、滾動及輸入停頓時自動截圖
- **輸入合併** — 合併連續按鍵，忽略沒有意義的滑鼠移動
- **單檔輸出** — 截圖以 base64 內嵌，一個 `.md` 檔包含完整流程
- **AI 友善格式** — 依時間排序操作，附帶座標、輸入內容與畫面證據
- **截圖容錯** — 某次畫面無法擷取時，仍會保留其他操作記錄並完成匯出

## 系統需求

### 直接使用 EXE

- Windows 10 或 Windows 11，64 位元
- 不需要另外安裝 Python

### 從原始碼執行

- Windows 10 或 Windows 11
- Python 3.11 或更新版本

## 最簡單的使用方法

如果你已取得建置完成的 `SkillRecorder.exe`：

1. 雙擊 `SkillRecorder.exe`
2. 按「開始錄製」
3. 示範一次你想教給 AI 的操作流程
4. 回到錄製視窗，按「停止並匯出」
5. 程式會顯示輸出位置
6. 按「開啟結果資料夾」即可找到 Markdown
7. 將 Markdown 交給 AI，請它理解流程並編寫對應技能

預設輸出位置：

```text
文件\Skill Recorder\
```

Git 倉庫不追蹤本機建置的 EXE。從 GitHub clone 原始碼的使用者，需依下方說明從原始碼執行，或先使用 `build_windows.cmd` 產生 EXE。正式發佈時可另外將 EXE 放入 GitHub Releases。

## 從原始碼安裝

```powershell
git clone https://github.com/chaneswin/skill-recorder-for-win.git
cd skill-recorder-for-win
python -m pip install -r requirements.txt
python recorder.py
```

可指定錄製標題與輸出位置：

```powershell
python recorder.py --title "部署網站流程" --output deploy_workflow.md
```

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-o, --output` | 輸出 Markdown 路徑 | `文件\Skill Recorder\skill_recording_日期時間.md` |
| `--title` | 寫入 Markdown 的錄製標題 | `Workflow Capture` |

## 建置 Windows EXE

雙擊：

```text
build_windows.cmd
```

建置完成的單檔執行程式位於：

```text
dist\SkillRecorder.exe
```

## 輸出格式

產生的 Markdown 包含錄製時間、結束時間、步驟數、總時長、給 AI 的任務說明、依序排列的操作資料及內嵌截圖。

簡化範例如下：

```markdown
# 部署網站流程

> Start: 2026-07-24 10:30:00
> End: 2026-07-24 10:30:08
> Steps: 2
> Duration: 8.0s

## 給 AI 的任務

請根據下方依時間排序的操作紀錄與畫面，理解這個工作流程……

## 原始流程紀錄

### Step 1: click
- Time: 0.0s
- x: 450
- y: 320
- button: left

![screenshot](data:image/jpeg;base64,...)

### Step 2: text
- Time: 1.3s
- text: hello world

![screenshot](data:image/jpeg;base64,...)
```

座標與輸入內容是當次示範留下的證據，AI 應先理解其意義，再決定如何寫成穩定的程式或技能，不應直接把畫面座標當成永久固定值。

## 隱私提醒

錄製期間會捕捉全域鍵盤輸入與螢幕畫面，可能記到密碼、Token、私人訊息或其他敏感資料。

請遵守：

- 錄製期間不要輸入密碼或敏感資料
- 開始前先關閉不相關的私人視窗
- 交給 AI 或公開分享前，先確認 Markdown 中的文字與截圖

所有錄製結果都儲存在本機；目前版本沒有雲端上傳功能。

## 專案結構

```text
skill-recorder-for-win/
├── recorder.py           # 程式入口與開始／停止／匯出流程
├── overlay.py            # Windows 原生控制視窗
├── event_capture.py      # 全域滑鼠與鍵盤事件監聽
├── screenshot.py         # 螢幕截圖與 JPEG 壓縮
├── exporter.py           # AI 友善 Markdown 匯出
├── models.py             # 錄製工作階段與事件資料模型
├── requirements.txt      # Python 執行相依套件
└── build_windows.cmd     # Windows EXE 建置入口
```

`SkillRecorder.exe`、`build/` 與 `dist/` 是本機建置產物，不提交至原始碼倉庫。

## 與原始 macOS 專案的關係

沿用的部分：

- 錄製真人操作並交給 AI 理解的產品概念
- 點擊、滾動、鍵盤輸入與截圖的事件模型
- Markdown 單檔輸出方向
- `recorder`、`overlay`、`event_capture`、`screenshot`、`exporter`、`models` 的模組劃分

Windows 重寫的部分：

- macOS CGEvent Tap 改為 `pynput` 全域事件監聽
- macOS AppKit 浮動按鈕改為 Win32 原生控制視窗
- Windows 多螢幕截圖與失敗容錯
- Windows 單檔 EXE 建置
- 錄製完成提示與結果資料夾入口

## 技術棧

- **[pynput](https://pynput.readthedocs.io/)** — Windows 全域滑鼠與鍵盤事件監聽
- **Win32 API / ctypes** — Windows 原生控制視窗
- **[mss](https://github.com/BoboTiG/python-mss)** — 螢幕截圖
- **[Pillow](https://python-pillow.org/)** — 圖片縮放與 JPEG 壓縮
- **[PyInstaller](https://pyinstaller.org/)** — Windows 單檔 EXE 打包

## 使用與相容性限制

- 目前提供的是 64 位元 Windows 10／11 單檔 EXE；32 位元 Windows 不支援
- 一般使用只需複製 `SkillRecorder.exe`，不需要原始碼或 Python
- EXE 尚未進行程式碼簽章，其他電腦第一次執行時可能出現 SmartScreen 或防毒軟體警告
- 部分公司或受管理電腦可能禁止全域鍵盤、滑鼠監聽
- 無法錄製 Windows 登入畫面、鎖定畫面或 UAC 安全桌面
- 若目標程式以系統管理員權限執行，錄製器也可能需要以系統管理員身分啟動
- 遠端桌面中斷、工作階段鎖定或特殊顯示環境下，螢幕截圖可能失敗；程式會盡量保留其他事件並完成匯出
- 目前記錄的是座標、鍵盤、滾動與截圖，不會讀取瀏覽器 DOM、CSS selector、XPath 或網頁元素語意
- 長流程會因內嵌 base64 截圖而產生較大的 Markdown 檔案
- 已在目前開發電腦完成 EXE 端到端測試；跨電腦相容性仍需更多實機驗證

## 目前版本

目前為 Windows MVP，已完成：

- Windows 原生介面啟動
- 滑鼠、滾動與鍵盤操作錄製
- 自動截圖
- AI 技能草稿匯出
- Windows 單檔 EXE

尚未包含 OCR、應用程式元件辨識、雲端同步或操作回放。

## 授權

MIT

---

# Skill Recorder for Windows

Record your operations once, let AI turn them into reusable skills.

Skill Recorder for Windows captures mouse clicks, keyboard input, and screenshots, then exports a structured Markdown file. Give the result to Claude, ChatGPT, Codex, or another AI so it can understand the workflow and help write code, document operating rules, or create a reusable Skill.

This project is the Windows port of [GrapeBear/skill-recorder](https://github.com/GrapeBear/skill-recorder). It preserves the original idea and module structure while replacing the macOS-specific event capture and user interface with Windows implementations.

This tool records workflows for AI understanding. It does not replay operations and is not an RPA runner.

## How It Works

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ You perform │────▶│   Windows    │────▶│  Markdown   │
│ a workflow  │     │   recorder   │     │ with images │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │ give to AI
                                                 ▼
                                          ┌─────────────┐
                                          │     AI      │
                                          │ understands │
                                          │ the workflow│
                                          │ & builds it │
                                          └─────────────┘
```

## Features

- **Native Windows control window** — start recording, stop and export, or open the result folder
- **Global event capture** — records mouse clicks, scrolling, and keyboard input
- **Smart screenshots** — captures the screen after clicks, scrolling, and typing pauses
- **Input batching** — combines consecutive keystrokes and ignores mouse movement noise
- **Self-contained output** — embeds screenshots as base64 in one Markdown file
- **AI-friendly structure** — chronological events with coordinates, input, and visual evidence
- **Capture fallback** — one failed screenshot does not abort the workflow recording

## Requirements

### Using the EXE

- 64-bit Windows 10 or Windows 11
- No separate Python installation required

### Running from Source

- Windows 10 or Windows 11
- Python 3.11 or newer

## Quick Start

If you already have a packaged `SkillRecorder.exe`:

1. Double-click `SkillRecorder.exe`
2. Click **Start Recording**
3. Demonstrate the workflow you want to teach the AI
4. Return to the recorder window and click **Stop and Export**
5. The application displays the saved file location
6. Click **Open Result Folder** to find the Markdown file
7. Give the Markdown file to an AI and ask it to understand and implement the skill

Default output folder:

```text
Documents\Skill Recorder\
```

The Git repository does not track locally built executables. Users who clone the source must run it with Python or use `build_windows.cmd` to create the EXE. A packaged EXE can be attached separately to GitHub Releases for distribution.

## Install from Source

```powershell
git clone https://github.com/chaneswin/skill-recorder-for-win.git
cd skill-recorder-for-win
python -m pip install -r requirements.txt
python recorder.py
```

Custom title and output path:

```powershell
python recorder.py --title "Website deployment workflow" --output deploy_workflow.md
```

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | Markdown output path | `Documents\Skill Recorder\skill_recording_TIMESTAMP.md` |
| `--title` | Recording title in the Markdown file | `Workflow Capture` |

## Build the Windows EXE

Double-click:

```text
build_windows.cmd
```

The packaged executable will be created at:

```text
dist\SkillRecorder.exe
```

## Output Format

The generated Markdown contains start and end times, step count, duration, instructions for the AI, chronological raw events, metadata, and embedded screenshots.

Simplified example:

```markdown
# Website deployment workflow

> Start: 2026-07-24 10:30:00
> End: 2026-07-24 10:30:08
> Steps: 2
> Duration: 8.0s

## Task for AI

Understand the following chronological operations and screen evidence...

## Raw Workflow Record

### Step 1: click
- Time: 0.0s
- x: 450
- y: 320
- button: left

![screenshot](data:image/jpeg;base64,...)

### Step 2: text
- Time: 1.3s
- text: hello world

![screenshot](data:image/jpeg;base64,...)
```

Coordinates and typed text are evidence from one demonstration. The AI should understand their meaning before turning the workflow into stable code or a reusable skill.

## Privacy Notice

The recorder captures global keyboard input and screen images while recording. This may include passwords, tokens, private messages, or other sensitive information.

- Do not type passwords or sensitive data while recording
- Close unrelated private windows before starting
- Review text and screenshots before sharing the Markdown file

All results stay on the local computer. The current version does not upload recordings to the cloud.

## Project Structure

```text
skill-recorder-for-win/
├── recorder.py           # Application entry and recording orchestration
├── overlay.py            # Native Windows control window
├── event_capture.py      # Global mouse and keyboard listeners
├── screenshot.py         # Screen capture and JPEG compression
├── exporter.py           # AI-friendly Markdown export
├── models.py             # Session and event data models
├── requirements.txt      # Python runtime dependencies
└── build_windows.cmd     # Windows EXE build entry
```

`SkillRecorder.exe`, `build/`, and `dist/` are local build artifacts and are not committed to the source repository.

## Relationship to the Original macOS Project

Inherited:

- The idea of recording a human workflow for AI understanding
- Click, scroll, keyboard, and screenshot event concepts
- Self-contained Markdown output
- The `recorder`, `overlay`, `event_capture`, `screenshot`, `exporter`, and `models` module split

Rewritten for Windows:

- macOS CGEvent Tap replaced with global `pynput` listeners
- macOS AppKit overlay replaced with a native Win32 control window
- Windows multi-monitor capture and screenshot failure fallback
- Single-file Windows EXE packaging
- Completion notification and result-folder shortcut

## Tech Stack

- **[pynput](https://pynput.readthedocs.io/)** — global mouse and keyboard capture
- **Win32 API / ctypes** — native Windows control window
- **[mss](https://github.com/BoboTiG/python-mss)** — screen capture
- **[Pillow](https://python-pillow.org/)** — image resizing and JPEG compression
- **[PyInstaller](https://pyinstaller.org/)** — single-file Windows packaging

## Usage and Compatibility Limitations

- The current package is a 64-bit Windows 10/11 executable; 32-bit Windows is not supported
- Normal use requires only `SkillRecorder.exe`; the source code and Python are not required
- The EXE is not code-signed, so SmartScreen or antivirus software may warn on first launch
- Managed or corporate computers may block global keyboard and mouse listeners
- Windows sign-in screens, locked sessions, and the UAC secure desktop cannot be recorded
- Recording an elevated application may require running the recorder as administrator
- Screenshots may fail after Remote Desktop disconnects, when the session is locked, or in unusual display environments; other events are preserved when possible
- The recorder stores coordinates, keyboard input, scrolling, and screenshots; it does not inspect browser DOM elements, CSS selectors, XPath, or element semantics
- Long recordings can produce large Markdown files because screenshots are embedded as base64
- The packaged EXE has passed an end-to-end test on the development computer; broader cross-machine compatibility testing is still pending

## Current Status

The Windows MVP includes:

- Native Windows interface
- Mouse, scroll, and keyboard recording
- Automatic screenshots
- AI skill-draft Markdown export
- Single-file Windows EXE

OCR, UI-element inspection, cloud sync, and operation replay are not included.

## License

MIT
