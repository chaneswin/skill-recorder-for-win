from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


EventKind = Literal["click", "scroll", "text"]


@dataclass(slots=True)
class RecordedEvent:
    kind: EventKind
    timestamp: datetime
    screenshot_b64: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RecordingSession:
    title: str
    started_at: datetime
    stopped_at: datetime | None = None
    events: list[RecordedEvent] = field(default_factory=list)

    def duration_seconds(self) -> float:
        end = self.stopped_at or datetime.now()
        return max(0.0, (end - self.started_at).total_seconds())
