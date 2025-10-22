# app/generator/model_generator.py

import os
import shutil
from datetime import datetime
from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_camel, map_pg_column_to_typescript
from pg_scaffold.preserve_custom.preservation import CodePreservationManager 

class TypescriptGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str, gen_version: str):
        output_dir = os.path.join(output_dir, "types")
        super().__init__(sql_json_dir, output_dir, "types.ts.j2",gen_version)

    # def write_code(self, rendered: str, output_dir: str, file_name: str) -> None:
    #     output_path = os.path.join(output_dir, file_name)        
    #     try:
    #         os.makedirs(os.path.dirname(output_path), exist_ok=True)
    #         with open(output_path, "w", encoding='utf-8') as f:
    #             f.write(rendered)
    #     except Exception as e:
    #         print(f"Error writing file {output_path}: {e}")  # Using print instead of logger
    #         raise

    def generate(self) -> None:        
        for table_name, table_info in self.schema.items():
            rendered = self.template.render(
                table_name = table_name,
                class_name = table_info["class_name"],
                columns = table_info.get("columns", []),
                snake_to_camel = snake_to_camel,
                map_pg_column_to_typescript = map_pg_column_to_typescript,
            )
            CodePreservationManager.write_code(rendered, self.output_dir, f"{table_info["file_name"]}.ts") 
            
            