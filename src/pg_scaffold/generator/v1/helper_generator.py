# app/generator/helper_generator.py

import os
import shutil
from pg_scaffold.generator.base import CodeGenerator

class HelperGenerator(CodeGenerator):
    def __init__(self, sql_json_dir: str, output_dir: str, gen_version: str):
        super().__init__(sql_json_dir, output_dir, None, gen_version)

    def generate(self) -> None:
        # Copy helper files
        src = os.path.join(self.template_dir, "run_app.sh")
        dst = os.path.join(self.output_dir, "run_app.sh")
        shutil.copy(src, dst)

        src = os.path.join(self.template_dir, "env")
        dst = os.path.join(self.output_dir, ".env")
        if not os.path.exists(dst):
            shutil.copy(src, dst)