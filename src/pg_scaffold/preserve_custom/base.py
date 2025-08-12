from typing import Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class PreservedCode:
    """Container for preserved custom code from a file."""
    file_path: str
    custom_code: str
    line_number: int = 0  # Line number where preservation block starts
    

class CodeExtractor(ABC):
    """Abstract base class for code extraction strategies."""
    
    @abstractmethod
    def extract_custom_code(self, content: str, file_path: str) -> Optional[PreservedCode]:
        """Extract custom code from file content."""
        pass
    
    @abstractmethod
    def is_generated_file(self, content: str, file_path: str) -> bool:
        """Check if file is a generated file."""
        pass
