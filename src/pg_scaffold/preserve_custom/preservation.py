import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pg_scaffold.preserve_custom.base import PreservedCode, PreservedBlock, CodeExtractor
from pg_scaffold.preserve_custom.pg_scaffolding import PgScaffoldingExtractor


class CodePreservationManager:
    """Manages multi-block custom code preservation and restoration across code generation cycles."""

    def __init__(self, source_directory: str, target_directory: Optional[str] = None,
                 extractor: Optional[CodeExtractor] = None):
        self.source_directory = Path(source_directory)
        self.target_directory = Path(target_directory) if target_directory else None
        self.extractor = extractor or PgScaffoldingExtractor()

        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def set_target_directory(self, target_directory: str) -> None:
        self.target_directory = Path(target_directory)

    def find_source_files(self, directory: Path) -> List[Path]:
        """Find all .py and .ts files in directory and subdirectories."""
        source_files = []
        try:
            for file_path in directory.rglob("*"):
                if file_path.suffix in {".py", ".ts"} and file_path.is_file():
                    source_files.append(file_path)
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
        return source_files

    # -------------------------------------------------------------------------
    # PRESERVATION PHASE
    # -------------------------------------------------------------------------
    def preserve_custom_code(self) -> Dict[str, PreservedCode]:
        """Scan source directory for custom code and extract all preserved sections."""
        preserved_code = {}

        if not self.source_directory.exists():
            print(f"Source directory not found: {self.source_directory}")
            return preserved_code

        python_files = self.find_source_files(self.source_directory)
        self.logger.info(f"Scanning {len(python_files)} Source files for custom code...")

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                relative_path = file_path.relative_to(self.source_directory)
                preserved = self.extractor.extract_custom_code(content, str(relative_path))
                if preserved and preserved.blocks:
                    preserved_code[str(relative_path)] = preserved
                    self.logger.info(f"Preserved {len(preserved.blocks)} block(s) from: {relative_path}")
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")

        self.logger.info(f"Preserved code from {len(preserved_code)} files")
        return preserved_code

    # -------------------------------------------------------------------------
    # RESTORATION PHASE
    # -------------------------------------------------------------------------
    def restore_custom_code(self, preserved_code: Dict[str, PreservedCode]) -> int:
        """Restore preserved code sections to target directory."""
        if not self.target_directory:
            raise ValueError("Target directory not set. Use set_target_directory() first.")
        if not self.target_directory.exists():
            raise FileNotFoundError(f"Target directory not found: {self.target_directory}")

        updated_count = 0
        python_files = self.find_source_files(self.target_directory)
        self.logger.info(f"Restoring custom code to {len(python_files)} files...")

        for file_path in python_files:
            try:
                relative_path = file_path.relative_to(self.target_directory)
                relative_path_str = str(relative_path)

                if relative_path_str in preserved_code:
                    if self._restore_to_file(file_path, preserved_code[relative_path_str]):
                        updated_count += 1
            except Exception as e:
                self.logger.error(f"Error restoring code to {file_path}: {e}")

        self.logger.info(f"Successfully restored custom code to {updated_count} files")
        return updated_count

    def _restore_to_file(self, file_path: Path, preserved: PreservedCode) -> bool:
        """Restore preserved code blocks to a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not self.extractor.is_generated_file(content, str(file_path)):
                self.logger.warning(f"Skipping non-generated file: {file_path}")
                return False

            new_content = self._insert_custom_code(content, preserved.blocks)
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.logger.info(f"Restored {len(preserved.blocks)} block(s) to: {file_path}")
                return True

        except Exception as e:
            self.logger.error(f"Error restoring to file {file_path}: {e}")
        return False

    # -------------------------------------------------------------------------
    # INSERTION LOGIC
    # -------------------------------------------------------------------------
    def _insert_custom_code(self, content: str, preserved_blocks: List[PreservedBlock]) -> str:
        """Insert all preserved blocks into corresponding labeled markers."""
        lines = content.split('\n')
        updated_lines = lines[:]

        for block in preserved_blocks:
            start_regex = re.compile(
                rf'^\s*(#|//)\s*#?-{{2}}\s*Preserve Custom code START(?:\s*:\s*{block.block_name})?\s*-{{2}}#?\s*$',
                re.MULTILINE
            )
            end_regex = re.compile(
                rf'^\s*(#|//)\s*#?-{{2}}\s*Preserve Custom code END(?:\s*:\s*{block.block_name})?\s*-{{2}}#?\s*$',
                re.MULTILINE
            )

            start_idx = next((i for i, line in enumerate(updated_lines) if start_regex.match(line)), None)
            end_idx = next((i for i, line in enumerate(updated_lines) if end_regex.match(line)), None)

            if start_idx is not None and end_idx is not None and end_idx > start_idx:
                new_block = block.custom_code.split('\n')
                updated_lines = (
                    updated_lines[:start_idx + 1] +
                    new_block +
                    updated_lines[end_idx:]
                )

        return '\n'.join(updated_lines)

    # -------------------------------------------------------------------------
    # WORKFLOW
    # -------------------------------------------------------------------------
    def preserve_and_restore(self, target_directory: str) -> Tuple[int, int]:
        """Complete workflow: preserve from source and restore to target."""
        preserved_code = self.preserve_custom_code()
        files_preserved = len(preserved_code)

        self.set_target_directory(target_directory)
        files_restored = self.restore_custom_code(preserved_code)
        return files_preserved, files_restored

    # -------------------------------------------------------------------------
    # UTILITY
    # -------------------------------------------------------------------------
    @staticmethod
    def write_code(rendered: str, output_dir: str, file_name: str) -> None:
        """Write generated code to file with pg-scaffolding markers and preservation blocks."""
        if Path(file_name).suffix == ".ts":
            comment_symbol = "//"
        else:
            comment_symbol = "#"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"{comment_symbol} # Generated by pg-scaffolding {timestamp}\n"

        # preserve_start = f"{comment_symbol} #-- Preserve Custom code START --#\n"
        # preserve_end = f"{comment_symbol} #-- Preserve Custom code END   --#\n"

        # full_content = header + rendered + "\n" + preserve_start + preserve_end
        full_content = header + rendered
        output_path = os.path.join(output_dir, file_name)

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding='utf-8') as f:
                f.write(full_content)
            print(f"Generated file: {output_path}")
        except Exception as e:
            print(f"Error writing file {output_path}: {e}")
            raise