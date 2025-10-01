# app/generator/model_generator.py

import os
import shutil
from pg_scaffold.generator.base import CodeGenerator

from pg_scaffold.generator.utils import map_pg_type_to_sqlalchemy_type, map_pg_column_to_sqlalchemy
from pg_scaffold.preserve_custom.preservation import CodePreservationManager 

class ModelGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str, gen_version: str):
        output_dir = os.path.join(output_dir, "app/models")
        super().__init__(sql_json_dir, output_dir, "model.py.j2",gen_version)
        src = os.path.join(self.template_dir, "model_base.py")
        dst = os.path.join(output_dir, "base.py")
        shutil.copyfile(src, dst)        

    def _get_relationships(self, table_schema: dict, relation_type: str ="foreign_key"):
        relationships = table_schema.get("relationships",[])
        relationships_of_type = [rel for rel in relationships if rel.get("relation_type") == relation_type] # type: ignore
        return relationships_of_type
        

    def _get_foreign_keys(self, table_schema):
        foreign_key_relationships = self._get_relationships(table_schema, "foreign_key")
        foreign_keys_dict = {}
        
        for fk in foreign_key_relationships:
            reference = f"{fk['referred_table']}.{fk['referred_column']}"
            foreign_keys_dict[fk["referred_variable"]] = f"ForeignKey('{reference}')" # type: ignore
            
        self.foreign_keys_dict = foreign_keys_dict
        return foreign_keys_dict

    def _get_foreign_key_for_column(self, column_name: str) -> str:
        """Return the ForeignKey string for a given column name."""
        foreign_key = self.foreign_keys_dict.get(column_name)
        if foreign_key:
            return f" {foreign_key},"
        return " "

    def generate_init(self) -> None:
        template = self._get_template("model__init__.py.j2")
        model_objects = [{"file_name":info["file_name"], "class_name":info["class_name"]} for info in self.schema.values()]
        rendered = template.render(
            model_objects = model_objects
        )
        
        output_path = os.path.join(self.output_dir, "__init__.py")
        with open(output_path, "w") as f:
            f.write(rendered)
            
            
    def generate(self) -> None:
        self.generate_init()
        for table_name, table_info in self.schema.items():
            self._get_foreign_keys(table_info)
            print(f"foreign_keys_dict: {self.foreign_keys_dict}")
            rendered = self.template.render(
                table_name = table_name,
                class_name = table_info["class_name"],
                columns = table_info.get("columns", []),
                relationships = table_info.get("relationships",[]),
                map_pg_type_to_sqlalchemy_type = map_pg_type_to_sqlalchemy_type,
                map_pg_column_to_sqlalchemy = map_pg_column_to_sqlalchemy,
                get_foreign_key_for_column = self._get_foreign_key_for_column
            )


            CodePreservationManager.write_code(rendered, self.output_dir, f"{table_info["file_name"]}.py")            