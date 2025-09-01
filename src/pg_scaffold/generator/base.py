# pg_scaffold/generator/base.py

import os
import glob
import json
from abc import ABC, abstractmethod
from typing import Any
from jinja2 import Environment, FileSystemLoader
from pg_scaffold.generator.utils import ensure_package_dirs

class CodeGenerator(ABC):
    """Abstract base class for code generators."""

    def __init__(self, sql_json_dir: Any, output_dir: str, template_file_nm: str, gen_version: str):
        self.sql_json_dir = sql_json_dir
        self.output_dir = output_dir
        print(f"Output directory: {self.output_dir}")
        ensure_package_dirs(self.output_dir, stop_at='app')
        
        self.schema = self._load_schema_from_dir(sql_json_dir)
        template_dir = os.path.join(os.path.dirname(__file__), f"{gen_version}/templates")
        self.template_dir = os.path.normpath(template_dir)
        
        self.template = self._get_template(template_file_nm)
        


    def _load_schema_from_dir(self, schema_dir: str):
        """Load all JSON files from the schema directory into self.schema"""
        metadata = {}

        json_files = glob.glob(os.path.join(schema_dir, "*.json"))
        for file_path in json_files:
            table_name = os.path.splitext(os.path.basename(file_path))[0]
            with open(file_path, "r", encoding="utf-8") as f:
                metadata[table_name] = json.load(f)
                
        return metadata

    def _get_template(self, template_file_nm):
        env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        return env.get_template(template_file_nm)
        
        
    @abstractmethod
    def generate(self) -> None:
        """Generate files using the extracted metadata."""
        pass