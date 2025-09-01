# app/generator/model_generator.py

import os

from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_pascal, map_pg_column_to_python
from pg_scaffold.preserve_custom.preservation import CodePreservationManager 

class APIGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str, gen_version: str):
        output_dir = os.path.join(output_dir, "api")
        super().__init__(sql_json_dir, output_dir, "api.py.j2")        

            
    def generate(self) -> None:
        for table_name, table_info in self.schema.items():
            
            rendered = self.template.render(
                table_name = table_name,
                class_name = table_info["class_name"],
                file_name = table_info["file_name"],
            )
            
            CodePreservationManager.write_code(rendered, self.output_dir, f"{table_info["file_name"]}.py")
            