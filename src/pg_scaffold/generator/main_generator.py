# app/generator/model_generator.py

import os
import shutil
from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_camel, map_pg_type_to_python
from pg_scaffold.generator.utils import ensure_package_dirs

class MainGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str):
        super().__init__(sql_json_dir, output_dir, "main.py.j2")
        core_dir = os.path.join(output_dir, "core")
        ensure_package_dirs(core_dir)
        src = os.path.join(self.template_dir, "core_db.py")
        dst = os.path.join(core_dir, "db.py")
        shutil.copyfile(src, dst)
            
    def generate(self) -> None:
        rendered = self.template.render(
            table_names = self.metadata.keys()
        )
        
        output_path = os.path.join(self.output_dir, "main.py")
        with open(output_path, "w") as f:
            f.write(rendered)