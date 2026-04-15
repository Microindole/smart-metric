from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class DiagramAdapter(ABC):
    name = "base"

    @abstractmethod
    def can_handle(self, filename: str, content: bytes) -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse(self, content: bytes) -> Dict:
        raise NotImplementedError
