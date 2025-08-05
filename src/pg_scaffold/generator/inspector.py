import os
import json
import sqlalchemy as sa
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from typing import Dict, List, Any, Optional


class DatabaseInspector:
    def __init__(self, db_url: str, output_dir: str):
        self.db_url = db_url
        self.output_dir = output_dir
        self.engine = self._create_engine()
        self.metadata: Optional[Dict[str, Any]] = None  # Will hold inspected metadata

    def _create_engine(self) -> Engine:
        return create_engine(self.db_url)

    def inspect(self) -> Dict[str, Any]:
        inspector = inspect(self.engine)
        metadata = {}

        for table_name in inspector.get_table_names():
            # Get PK constraint
            pk_info = inspector.get_pk_constraint(table_name)
            primary_keys = pk_info.get("constrained_columns", [])

            indexes = inspector.get_indexes(table_name)
            index_columns = [col for index in indexes for col in index.get("column_names", [])]
            unique_columns = [col for index in indexes if index.get("unique") for col in index.get("column_names", [])]

            column_info = []
            for col in inspector.get_columns(table_name):
                print(f"Inspecting column: {col}")
                column_info.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "server_default": True if col["default"] is not None else False,
                    "index": col["name"] in index_columns,
                    "unique": col["name"] in unique_columns,
                    "primary_key": col["name"] in primary_keys,
                    "indexed": col["name"] in index_columns or col["name"] in primary_keys,
                })

            fk_info = []
            for fk in inspector.get_foreign_keys(table_name):
                fk_info.append({
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                })

            metadata[table_name] = {
                "table_name": table_name,
                "columns": column_info,
                "foreign_keys": fk_info,
            }

        self.metadata = metadata  # Save metadata in the instance
        return metadata

    def generate_json(self) -> None:
        """Writes one JSON file per table in the output_dir."""
        if self.metadata is None:
            self.inspect()

        metadata_dir = os.path.join(self.output_dir, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)

        for table_name, table_data in self.metadata.items():
            #print(f"Writing metadata JSON files to: {table_data}")
            #print("*" * 40)
            file_path = os.path.join(metadata_dir, f"{table_name}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(table_data, f, indent=2)

        print(f"Metadata JSON files written to: {metadata_dir}")