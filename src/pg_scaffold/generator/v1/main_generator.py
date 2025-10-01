# app/generator/model_generator.py

import os
import shutil
from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_pascal, map_pg_column_to_python
from pg_scaffold.preserve_custom.preservation import CodePreservationManager 

class MainGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str, gen_version: str):
        self.main_dir = output_dir
        output_dir = os.path.join(output_dir, "app/core")
        super().__init__(sql_json_dir, output_dir, "main.py.j2",gen_version)
        src = os.path.join(self.template_dir, "core_db.py")
        dst = os.path.join(output_dir, "db.py")
        shutil.copyfile(src, dst)
            
    def generate(self) -> None:
        file_names = [info["file_name"] for info in self.schema.values()]
        
        rendered = self.template.render(
            file_names = file_names
        )
        
        CodePreservationManager.write_code(rendered, self.main_dir, "main.py")            