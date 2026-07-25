from __future__ import annotations

import threading
from datetime import datetime
from typing import Optional

from pynput import keyboard, mouse

from models import RecordedEvent, RecordingSession
from screenshot import capture_screen_b64


class EventCapture:
    def __init__(self, session: RecordingSession):
        self.session = session
        self._recording = False
        self._lock = threading.Lock()
        self._text_buffer: list[str] = []
        self._flush_timer: Optional[threading.Timer] = None
        self._mouse_listener: mouse.Listener | None = None
        self._keyboard_listener: keyboard.Listener | None = None

    def start(self) -> None:
        if self._mouse_listener or self._keyboard_listener:
            return
        self._mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self) -> None:
        self._recording = False
        self._flush_text_buffer()
        if self._flush_timer:
            self._flush_timer.cancel()
            self._flush_timer = None
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

    def set_recording(self, value: bool) -> None:
        self._recording = value
        if not value:
            self._flush_text_buffer()

    def _append_event(self, kind: str, **meta: object) -> None:
        self.session.events.append(
            RecordedEvent(
                kind=kind,  # type: ignore[arg-type]
                timestamp=datetime.now(),
                screenshot_b64=capture_screen_b64(),
                meta={k: v for k, v in meta.items() if v is not None},
            )
        )

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if not self._recording or not pressed:
            return
        self._flush_text_buffer()
        self._append_event(
            "click",
            x=x,
            y=y,
            button=getattr(button, "name", str(button)),
        )

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        if not self._recording:
            return
        self._flush_text_buffer()
        self._append_event("scroll", x=x, y=y, dx=dx, dy=dy)

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if not self._recording:
            return
        text = self._normalize_key(key)
        if text is None:
            return
        with self._lock:
            self._text_buffer.append(text)
        if len(self._text_buffer) == 1:
            self._schedule_flush()

    def _on_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if not self._recording:
            return
        if key == keyboard.Key.enter:
            self._flush_text_buffer()

    def _normalize_key(self, key: keyboard.Key | keyboard.KeyCode) -> str | None:
        if isinstance(key, keyboard.KeyCode):
            return key.char
        special = {
            keyboard.Key.space: " ",
            keyboard.Key.enter: "<enter>",
            keyboard.Key.tab: "<tab>",
            keyboard.Key.backspace: "<backspace>",
            keyboard.Key.esc: "<esc>",
        }
        return special.get(key)

    def _schedule_flush(self) -> None:
        if self._flush_timer:
            self._flush_timer.cancel()
        self._flush_timer = threading.Timer(0.8, self._flush_text_buffer)
        self._flush_timer.daemon = True
        self._flush_timer.start()

    def _flush_text_buffer(self) -> None:
        with self._lock:
            if not self._text_buffer:
                return
            text = "".join(self._text_buffer)
            self._text_buffer.clear()
        self._append_event("text", text=text)
