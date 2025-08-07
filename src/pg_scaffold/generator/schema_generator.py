# app/generator/model_generator.py

import os

from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_pascal, map_pg_type_to_python


class SchemaGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str):
        output_dir = os.path.join(output_dir, "schemas")
        super().__init__(sql_json_dir, output_dir, "schema.py.j2")
        

            
    def generate(self) -> None:
        for table_name, table_info in self.schema.items():
            
            rendered = self.template.render(
                table_name = table_name,
                class_name = table_info["class_name"],
                columns = table_info.get("columns", []),
                map_pg_type_to_python = map_pg_type_to_python,
            )
            
            output_path = os.path.join(self.output_dir, f"{table_info["file_name"]}.py")
            with open(output_path, "w") as f:
                f.write(rendered)