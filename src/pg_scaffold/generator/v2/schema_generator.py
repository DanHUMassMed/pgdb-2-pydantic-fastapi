# app/generator/model_generator.py

import os
import shutil
from pg_scaffold.generator.base import CodeGenerator
from pg_scaffold.generator.utils import snake_to_pascal, map_pg_column_to_python
from pg_scaffold.preserve_custom.preservation import CodePreservationManager 

class SchemaGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str, gen_version: str):
        output_dir = os.path.join(output_dir, "app/schemas")
        super().__init__(sql_json_dir, output_dir, "schema.py.j2",gen_version)
        src = os.path.join(self.template_dir, "schema_base.py")
        dst = os.path.join(output_dir, "base.py")
        shutil.copyfile(src, dst)           
        # src = os.path.join(self.template_dir, "schema__init__.py")
        # dst = os.path.join(output_dir, "__init__.py")
        # shutil.copyfile(src, dst)           

    def generate_init(self) -> None:
        template = self._get_template("schema__init__.py.j2")
        model_objects = [{"file_name":info["file_name"], 
                         "class_name":info["class_name"],
                         "has_relationships": (len(info.get("relationships",[])) > 0)}
                            for info in self.schema.values()]
        model_objects = sorted(model_objects, key=lambda x: x["file_name"])
        rendered = template.render(
            model_objects = model_objects
        )
        
        output_path = os.path.join(self.output_dir, "__init__.py")
        with open(output_path, "w") as f:
            f.write(rendered)

    def generate(self) -> None:
        self.generate_init()
        for table_name, table_info in self.schema.items():
            
            rendered = self.template.render(
                table_name = table_name,
                class_name = table_info["class_name"],
                columns = table_info.get("columns", []),
                relationships = table_info.get("relationships",[]),
                map_pg_column_to_python = map_pg_column_to_python,
            )
            
            CodePreservationManager.write_code(rendered, self.output_dir, f"{table_info["file_name"]}.py")            