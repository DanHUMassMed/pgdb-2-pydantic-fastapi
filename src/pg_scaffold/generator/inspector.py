import logging
import os
import json
import sqlalchemy as sa
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any, Optional
from pg_scaffold.generator.utils import table_name_to_class_name, table_name_to_variable_name, table_name_to_file_name

class DatabaseInspector:
    def __init__(self, db_url: str, output_dir: str):
        self.db_url = db_url
        self.output_dir = output_dir
        self.engine = self._create_engine(db_url)
        self.inspector = inspect(self.engine)
        self.schema: Optional[Dict[str, Any]] = None  # Will hold inspected metadata

    def _create_engine(self, db_url: str) -> Engine:
        try:
            engine = create_engine(db_url)
            # Optionally test the connection
            with engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
            return engine
        except SQLAlchemyError as e:
            logging.exception("Failed to create SQLAlchemy engine or connect to the database.")
            raise RuntimeError(f"Error connecting to the database: {e}")

    def _tables_for_scheme(self):
        self.schema = {}
        for table_name in self.inspector.get_table_names():
            self.schema[table_name] = { 
                                       "table_name": table_name,
                                       "class_name" : table_name_to_class_name(table_name),
                                       "file_name": table_name_to_file_name(table_name),
                                       "columns": [],
                                       "relationships": []
                                       } # type: ignore
            
            
    def _columns_for_table(self, table_name: str):
        columns = []
        pk_constraint = self.inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get("constrained_columns", [])

        indexes = self.inspector.get_indexes(table_name)
        index_columns  = [col for index in indexes for col in index.get("column_names", [])]
        unique_columns = [col for index in indexes if index.get("unique") for col in index.get("column_names", [])]

        for column_name in self.inspector.get_columns(table_name):
            #print(f"Inspecting column: {column_name}")
            columns.append({
                "name": column_name["name"],
                "type": str(column_name["type"]),
                "nullable": column_name["nullable"],
                "server_default": True if column_name["default"] is not None else False,
                "index": column_name["name"] in index_columns,
                "unique": column_name["name"] in unique_columns,
                "primary_key": column_name["name"] in primary_keys,
                "indexed": column_name["name"] in index_columns or column_name["name"] in primary_keys,
            })

        return columns
    
    def _relationships_for_table(self, table_name: str):
        relationships = []
        reverse_relationships = []
        unique_constraints = self.inspector.get_unique_constraints(table_name)
        pk_constraint = self.inspector.get_pk_constraint(table_name)

        unique_cols = {col for uc in unique_constraints for col in uc["column_names"]}
        pk_cols = set(pk_constraint.get("constrained_columns", []))

        for fk in self.inspector.get_foreign_keys(table_name):
            constrained_columns = fk["constrained_columns"]
            referred_columns = fk["referred_columns"]

            if len(constrained_columns) != 1 or len(referred_columns) != 1:
                raise ValueError(
                    f"Expected 1:1 column mapping in foreign key for table '{table_name}', got: {fk}"
                )

            constrained_col = constrained_columns[0]
            referred_col = referred_columns[0]
            referred_table = fk["referred_table"]

            # Determine if it's a one-to-one by checking for uniqueness
            is_one_to_one = (
                constrained_col in unique_cols or constrained_col in pk_cols
            )
            print(f"is one-to-one: {is_one_to_one} for {constrained_col} in {table_name}")
            relationships.append({
                "relationship_table_name": table_name,
                "related_file_name": table_name_to_file_name(referred_table),
                "related_model": table_name_to_class_name(referred_table),
                "relationship_variable": table_name_to_variable_name(referred_table, use_singular = True),
                "back_populates": table_name_to_variable_name(table_name, use_singular = is_one_to_one),
                "use_list": not is_one_to_one,  # False means one-to-one
                
                "referred_table": referred_table,
                "referred_column": referred_col,
                "constrained_column": constrained_col,
                "relation_type": "foreign_key",  # ← added type info
            })

            reverse_relationships.append({
                "relationship_table_name": referred_table,
                "relationship_file_name": table_name_to_file_name(referred_table),
                "related_file_name": table_name_to_file_name(table_name),
                "related_model": table_name_to_class_name(table_name),
                "relationship_variable": table_name_to_variable_name(table_name, use_singular=is_one_to_one),
                "back_populates": table_name_to_variable_name(referred_table, use_singular=True),
                "use_list": not is_one_to_one,  # Reverse is always one-to-many unless overridden manually
                "relation_type": "reverse",  # ← added type info
            })

        return relationships, reverse_relationships
        
        
    def inspect(self) -> Dict[str, Any]:
        
        self._tables_for_scheme()

        reverse_relationships = []
        for table_name in self.schema.keys(): # type: ignore
            print(f"Inspecting table: {table_name}")
            columns_info = self._columns_for_table(table_name)
            foreign_key, reverse = self._relationships_for_table(table_name)

            self.schema[table_name]["columns"].extend(columns_info) # type: ignore
            self.schema[table_name]["relationships"].extend(foreign_key) # type: ignore
            reverse_relationships.extend(reverse) # type: ignore
            
        for relationship in reverse_relationships:
            owner = relationship["relationship_table_name"]
            self.schema[owner]["relationships"].append(relationship)  # type: ignore
                
        return self.schema # type: ignore

    def generate_scheme_json(self) -> None:
        """Writes one JSON file per table in the output_dir."""
        if self.schema is None:
            self.inspect()

        metadata_dir = os.path.join(self.output_dir, "schema_json")
        os.makedirs(metadata_dir, exist_ok=True)

        for table_name, table_data in self.schema.items():
            #print(f"Writing metadata JSON files to: {table_data}")
            #print("*" * 40)
            file_path = os.path.join(metadata_dir, f"{table_name}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(table_data, f, indent=2)

        print(f"Metadata JSON files written to: {metadata_dir}")