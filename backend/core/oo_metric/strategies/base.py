from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class SourceClassInfo:
    name: str
    parent: str = ""
    body: str = ""
    language: str = ""
    fields: Set[str] = field(default_factory=set)
    methods: Dict[str, str] = field(default_factory=dict)
    references: Set[str] = field(default_factory=set)


class SourceAnalyzer(ABC):
    language: str

    @abstractmethod
    def analyze(self, filename: str, text: str) -> List[Dict]:
        raise NotImplementedError
