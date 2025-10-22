import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pg_scaffold.preserve_custom.base import CodeExtractor, PreservedCode
from pg_scaffold.preserve_custom.pg_scaffolding import PgScaffoldingExtractor

class CodePreservationManager:
    """Main class for managing custom code preservation across code generation cycles."""
    
    def __init__(self, source_directory: str, target_directory: Optional[str] = None, 
                 extractor: Optional[CodeExtractor] = None):
        """
        Initialize the preservation manager.
        
        Args:
            source_directory: Directory containing existing code with custom sections
            target_directory: Directory containing newly generated code (optional)
            extractor: Code extraction strategy (defaults to PgScaffoldingExtractor)
        """
        self.source_directory = Path(source_directory)
        self.target_directory = Path(target_directory) if target_directory else None
        self.extractor = extractor or PgScaffoldingExtractor()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def set_target_directory(self, target_directory: str) -> None:
        """Set the target directory for code restoration."""
        self.target_directory = Path(target_directory)
    
    def find_source_files(self, directory: Path) -> List[Path]:
        """Find all source files in directory and subdirectories."""
        source_files = []
        try:
            for file_path in directory.rglob("*"):
                if file_path.suffix in {".py", ".ts"}:
                    if file_path.is_file():
                        source_files.append(file_path)
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
        
        return source_files
    
    def preserve_custom_code(self) -> Dict[str, PreservedCode]:
        """
        Scan source directory for generated files and extract custom code.
        
        Returns:
            Dictionary mapping relative file paths to preserved code objects
        """
        preserved_code = {}
        
        if not self.source_directory.exists():
            print(f"Source directory not found: {self.source_directory}")
            return preserved_code
        
        python_files = self.find_source_files(self.source_directory)
        self.logger.info(f"Scanning {len(python_files)} Source files for custom code...")
        
        for file_path in python_files:
            print(f"scanning {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get relative path for consistent key generation
                relative_path = file_path.relative_to(self.source_directory)
                
                preserved = self.extractor.extract_custom_code(content, str(relative_path))
                if preserved:
                    preserved_code[str(relative_path)] = preserved
                    self.logger.info(f"Preserved custom code from: {relative_path}")
                    
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
        
        self.logger.info(f"Preserved custom code from {len(preserved_code)} files")
        return preserved_code
    
    def restore_custom_code(self, preserved_code: Dict[str, PreservedCode]) -> int:
        """
        Restore preserved custom code to files in target directory.
        
        Args:
            preserved_code: Dictionary of preserved code from preserve_custom_code()
            
        Returns:
            Number of files successfully updated
        """
        if not self.target_directory:
            raise ValueError("Target directory not set. Use set_target_directory() first.")
        
        if not self.target_directory.exists():
            raise FileNotFoundError(f"Target directory not found: {self.target_directory}")
        
        updated_count = 0
        python_files = self.find_source_files(self.target_directory)
        
        self.logger.info(f"Restoring custom code to {len(python_files)} Python files...")
        
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
        """Restore custom code to a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify this is a generated file
            if not self.extractor.is_generated_file(content, str(file_path)):
                self.logger.warning(f"Skipping non-generated file: {file_path}")
                return False
            
            # Find preservation markers and insert custom code
            new_content = self._insert_custom_code(content, preserved.custom_code)
            
            if new_content != content:
                # # Create backup
                # backup_path = file_path.with_suffix('.py.backup')
                # with open(backup_path, 'w', encoding='utf-8') as f:
                #     f.write(content)
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.logger.info(f"Restored custom code to: {file_path}")
                return True
            
        except Exception as e:
            self.logger.error(f"Error restoring to file {file_path}: {e}")
        
        return False
    
    def _insert_custom_code(self, content: str, custom_code: str) -> str:
        """Insert custom code between preservation markers."""
        lines = content.split('\n')
        start_pattern = re.compile(self.extractor.PRESERVE_START, re.MULTILINE | re.IGNORECASE)
        end_pattern = re.compile(self.extractor.PRESERVE_END, re.MULTILINE | re.IGNORECASE)
        
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if start_pattern.match(line):
                start_idx = i
            elif end_pattern.match(line) and start_idx is not None:
                end_idx = i
                break
        
        if start_idx is not None and end_idx is not None:
            # Replace content between markers
            new_lines = (lines[:start_idx + 1] + 
                        custom_code.split('\n') + 
                        lines[end_idx:])
            return '\n'.join(new_lines)
        
        return content
    
    def preserve_and_restore(self, target_directory: str) -> Tuple[int, int]:
        """
        Complete workflow: preserve from source and restore to target.
        
        Args:
            target_directory: Directory with newly generated code
            
        Returns:
            Tuple of (files_preserved_from, files_restored_to)
        """
        preserved_code = self.preserve_custom_code()
        files_preserved = len(preserved_code)
        
        self.set_target_directory(target_directory)
        files_restored = self.restore_custom_code(preserved_code)
        
        return files_preserved, files_restored
    
    @staticmethod
    def write_code(rendered: str, output_dir: str, file_name: str) -> None:
        """
        Write generated code to file with pg-scaffolding markers and preservation blocks.
        
        Args:
            rendered: The generated code content to write
            output_dir: Directory where the file should be written
            table_info: Dictionary containing file information, must have 'file_name' key
        """
        if Path(file_name).suffix == ".ts":
            comment_symbol = "//"
        else:
            comment_symbol = "#"
        
        # Generate timestamp for header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"{comment_symbol} # Generated by pg-scaffolding {timestamp}\n"
        
        # Preservation markers
        preserve_start = f"{comment_symbol} #-- Preserve Custom code START --#\n"
        preserve_end = f"{comment_symbol} #-- Preserve Custom code END   --#\n"
        
        # Combine all parts
        full_content = header + rendered + "\n" + preserve_start + preserve_end
        
        # Write to file
        output_path = os.path.join(output_dir, file_name)
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding='utf-8') as f:
                f.write(full_content)
            
            print(f"Generated file: {output_path}")  # Using print instead of logger
            
        except Exception as e:
            print(f"Error writing file {output_path}: {e}")  # Using print instead of logger
            raise


