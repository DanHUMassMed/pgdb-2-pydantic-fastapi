# app/generator/model_generator.py

import os

from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_camel, map_pg_type_to_python


class APIGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str):
        output_dir = os.path.join(output_dir, "api/v1")
        super().__init__(sql_json_dir, output_dir, "api.py.j2")        

            
    def generate(self) -> None:
        for table_name, info in self.metadata.items():
            
            rendered = self.template.render(
                table_name = table_name,
                class_name = snake_to_camel(table_name),
            )
            
            output_path = os.path.join(self.output_dir, f"{table_name}.py")
            print(f"Writing API file for {table_name} to: {output_path}")
            with open(output_path, "w") as f:
                f.write(rendered)