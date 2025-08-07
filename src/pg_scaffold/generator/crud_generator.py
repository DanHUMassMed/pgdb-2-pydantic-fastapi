# app/generator/model_generator.py

import os
import shutil
from jinja2 import Environment, FileSystemLoader
from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_pascal, map_pg_type_to_python



class CRUDGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str):
        output_dir = os.path.join(output_dir, "crud")
        super().__init__(sql_json_dir, output_dir, "crud.py.j2")
        src = os.path.join(self.template_dir, "crud_base.py")
        dst = os.path.join(output_dir, "base.py")
        shutil.copyfile(src, dst)

            
    def generate(self) -> None:
        for table_name, info in self.schema.items():
            
            rendered = self.template.render(
                table_name = table_name,
                class_name = snake_to_pascal(table_name),
            )
            
            output_path = os.path.join(self.output_dir, f"{table_name}.py")
            with open(output_path, "w") as f:
                f.write(rendered)