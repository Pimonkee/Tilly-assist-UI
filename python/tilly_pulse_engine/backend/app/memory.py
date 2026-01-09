from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Deque, List

from .models import Interaction


class RollingMemory:
    """
    Dumb but effective: keeps a small history window in RAM.
    You can later swap this for Redis / Mongo / Postgres.
    """

    def __init__(self, maxlen: int = 200):
        self._events: Deque[Interaction] = deque(maxlen=maxlen)

    def add(self, interaction: Interaction) -> None:
        if interaction.timestamp is None:
            interaction.timestamp = datetime.utcnow()
        self._events.append(interaction)

    def history(self) -> List[Interaction]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()
