from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class PreservedBlock:
    """One preserved region within a file."""
    block_name: str        # Label or identifier for the block (e.g. "setup", "validate")
    custom_code: str       # The preserved code content
    start_line: int        # Start line (after START marker)
    end_line: int          # End line (before END marker)


@dataclass
class PreservedCode:
    """Container for all preserved regions in a single file."""
    file_path: str
    blocks: List[PreservedBlock]


class CodeExtractor(ABC):
    """Abstract base class for code extraction strategies."""

    @abstractmethod
    def extract_custom_code(self, content: str, file_path: str) -> PreservedCode | None:
        """Extract all preserved custom code blocks from file content."""
        pass

    @abstractmethod
    def is_generated_file(self, content: str, file_path: str) -> bool:
        """Check if file is a generated file."""
        pass