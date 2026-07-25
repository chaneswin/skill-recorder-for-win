from __future__ import annotations

from pathlib import Path

from models import RecordingSession


def _format_offset(start, current) -> str:
    return f"{(current - start).total_seconds():.1f}s"


def export_markdown(session: RecordingSession, output_path: str | Path) -> str:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(f"# {session.title}")
    lines.append("")
    lines.append(f"> Start: {session.started_at:%Y-%m-%d %H:%M:%S}")
    if session.stopped_at:
        lines.append(f"> End: {session.stopped_at:%Y-%m-%d %H:%M:%S}")
    lines.append(f"> Steps: {len(session.events)}")
    lines.append(f"> Duration: {session.duration_seconds():.1f}s")
    lines.append("")
    lines.append("## 給 AI 的任務")
    lines.append("")
    lines.append(
        "請根據下方依時間排序的操作紀錄與畫面，理解這個工作流程，"
        "整理出目標、前置條件、操作步驟、判斷規則、例外處理與完成條件，"
        "再將它改寫成可重複使用的程式設計技能或代理人操作說明。"
    )
    lines.append("")
    lines.append("注意：座標與輸入內容是當次示範的證據，不應直接當成永久固定值。")
    lines.append("")
    lines.append("## 原始流程紀錄")
    lines.append("")

    for index, event in enumerate(session.events, start=1):
        lines.append(f"### Step {index}: {event.kind}")
        lines.append(f"- Time: {_format_offset(session.started_at, event.timestamp)}")
        for key, value in event.meta.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
        if event.screenshot_b64:
            lines.append(f"![screenshot](data:image/jpeg;base64,{event.screenshot_b64})")
            lines.append("")

    output.write_text("\n".join(lines), encoding="utf-8")
    return str(output)
