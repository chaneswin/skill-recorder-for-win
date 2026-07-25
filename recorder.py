#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from event_capture import EventCapture
from exporter import export_markdown
from models import RecordingSession
from overlay import Overlay


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Skill Recorder for Windows")
    parser.add_argument(
        "-o",
        "--output",
        help="Markdown output path. Default: recording_YYYYMMDD_HHMMSS.md",
    )
    parser.add_argument(
        "--title",
        default="Workflow Capture",
        help="Recording title written into the Markdown header.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    session = RecordingSession(title=args.title, started_at=datetime.now())
    capture = EventCapture(session=session)
    capture.start()
    is_recording = False

    def current_output_path() -> Path:
        if args.output:
            return Path(args.output)
        return (
            Path.home()
            / "Documents"
            / "Skill Recorder"
            / f"skill_recording_{datetime.now():%Y%m%d_%H%M%S}.md"
        )

    def start_recording() -> None:
        nonlocal is_recording
        session.started_at = datetime.now()
        session.stopped_at = None
        session.events.clear()
        capture.set_recording(True)
        is_recording = True
        print("Recording started.")

    def stop_recording() -> str | None:
        nonlocal is_recording
        if not is_recording:
            return None
        session.stopped_at = datetime.now()
        capture.set_recording(False)
        is_recording = False
        saved_path = export_markdown(session, current_output_path())
        print(f"Exported to: {saved_path}")
        return str(Path(saved_path).resolve())

    def quit_app() -> None:
        if is_recording:
            stop_recording()
        capture.stop()

    overlay = Overlay(
        on_start=start_recording,
        on_stop=stop_recording,
        on_quit=quit_app,
    )
    overlay.show()


if __name__ == "__main__":
    main()
