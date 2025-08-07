# app/generator/model_generator.py

import os
import shutil
from pg_scaffold.generator.base import CodeGenerator

from pg_scaffold.generator.utils import table_name_to_class_name, map_pg_type_to_sqlalchemy

class ModelGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str):
        output_dir = os.path.join(output_dir, "models")
        super().__init__(sql_json_dir, output_dir, "model.py.j2")
        src = os.path.join(self.template_dir, "model_base.py")
        dst = os.path.join(output_dir, "base.py")
        shutil.copyfile(src, dst)        

    def _get_relationships(self, table_schema: dict, relation_type: str ="foreign_key"):
        relationships = table_schema.get("relationships",[])
        relationships_of_type = [rel for rel in relationships if rel.get("relation_type") == relation_type] # type: ignore
        return relationships_of_type
        
    def _create_imports(self, table_schema: dict) -> str:
        """Create SQLAlchemy import string based on table schema."""
        type_set = set()

        # 1. Process column types
        for column in table_schema.get("columns", []):
            pg_type = column["type"]
            sqlalchemy_type = map_pg_type_to_sqlalchemy(pg_type)
            type_set.add(sqlalchemy_type)

        # 2. Add ForeignKey if foreign keys exist
        if self._get_relationships(table_schema, "foreign_key"):
            type_set.add("ForeignKey")

        # 3. Ensure 'Column' is present in final import line
        full_imports = ["Column"] + sorted(type_set)
        return ", ".join(full_imports)

    def _get_foreign_keys(self, table_schema):
        foreign_key_relationships = self._get_relationships(table_schema, "foreign_key")
        foreign_keys_dict = {}
        
        for fk in foreign_key_relationships:
            reference = f"{fk['referred_table']}.{fk['referred_column']}"
            foreign_keys_dict[fk["constrained_column"]] = f"ForeignKey('{reference}')" # type: ignore
            
        self.foreign_keys_dict = foreign_keys_dict
        return foreign_keys_dict

    def _get_foreign_key_for_column(self, column_name: str) -> str:
        """Return the ForeignKey string for a given column name."""
        foreign_key = self.foreign_keys_dict.get(column_name)
        if foreign_key:
            return f", {foreign_key}"
        return ""

            
    def generate(self) -> None:

        for table_name, table_info in self.schema.items():
            self._get_foreign_keys(table_info)
            print(f"foreign_keys_dict: {self.foreign_keys_dict}")
            rendered = self.template.render(
                table_name = table_name,
                class_name = table_info["class_name"],
                columns = table_info.get("columns", []),
                relationships = table_info.get("relationships",[]),
                sqlalchemy_imports = self._create_imports(table_info),
                map_pg_type_to_sqlalchemy = map_pg_type_to_sqlalchemy,
                get_foreign_key_for_column = self._get_foreign_key_for_column
            )

            output_path = os.path.join(self.output_dir, f"{table_info["file_name"]}.py")
            with open(output_path, "w") as f:
                f.write(rendered)