from abc import ABC, abstractmethod
from pathlib import Path


class DocumentLoader(ABC):
    @abstractmethod
    def load(self, source: Path) -> str:
        """Extract text from a document source."""
        raise NotImplementedError