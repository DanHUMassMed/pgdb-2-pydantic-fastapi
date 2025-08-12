# app/generator/model_generator.py

import os
import shutil
from jinja2 import Environment, FileSystemLoader
from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_pascal, map_pg_column_to_python
from pg_scaffold.preserve_custom.preservation import CodePreservationManager 


class CRUDGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str):
        output_dir = os.path.join(output_dir, "crud")
        super().__init__(sql_json_dir, output_dir, "crud.py.j2")
        src = os.path.join(self.template_dir, "crud_base.py")
        dst = os.path.join(output_dir, "base.py")
        shutil.copyfile(src, dst)

            
    def generate(self) -> None:
        for table_name, table_info in self.schema.items():
            print(f"relationships: {table_info.get("relationships",[])}")
            rendered = self.template.render(
                table_name = table_name,
                file_name = table_info["file_name"],
                class_name = table_info["class_name"],
                relationships = table_info.get("relationships",[]),
            )
            
            CodePreservationManager.write_code(rendered, self.output_dir, f"{table_info["file_name"]}.py")