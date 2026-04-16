from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import Namespace, _SubParsersAction
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class CliContext:
    lang: str
    catalog: Dict


class BaseCommand(ABC):
    path: Tuple[str, ...]

    @property
    def key(self) -> str:
        return ".".join(self.path)

    @abstractmethod
    def configure(self, subparsers: _SubParsersAction, ctx: CliContext) -> None:
        raise NotImplementedError

    @abstractmethod
    def run(self, args: Namespace, ctx: CliContext) -> int:
        raise NotImplementedError
