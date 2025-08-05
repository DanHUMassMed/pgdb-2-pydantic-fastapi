# app/generator/model_generator.py

import os

from pg_scaffold.generator.base import CodeGenerator

from pg_scaffold.generator.utils import snake_to_camel,map_pg_type_to_sqlalchemy

class ModelGenerator(CodeGenerator):
    
    def __init__(self, sql_json_dir: str, output_dir: str):
        output_dir = os.path.join(output_dir, "models")
        super().__init__(sql_json_dir, output_dir, "model.py.j2")
        

    def _create_imports(self, table_schema: dict) -> str:
        """Create SQLAlchemy import string based on table schema."""
        type_set = set()

        # 1. Process column types
        for column in table_schema.get("columns", []):
            pg_type = column["type"]
            sqlalchemy_type = map_pg_type_to_sqlalchemy(pg_type)
            type_set.add(sqlalchemy_type)

        # 2. Add ForeignKey if foreign keys exist
        if table_schema.get("foreign_keys"):
            type_set.add("ForeignKey")

        # 3. Ensure 'Column' is present in final import line
        full_imports = ["Column"] + sorted(type_set)
        return ", ".join(full_imports)

    def _get_foreign_keys(self, foreign_keys_json):
        foreign_keys_dict = {}
        
        for fk in foreign_keys_json:
            for constrained_col, referred_col in zip(
                fk["constrained_columns"], fk["referred_columns"]
            ):
                reference = f"{fk['referred_table']}.{referred_col}"
                foreign_keys_dict[constrained_col] = f"ForeignKey('{reference}')"
        self.foreign_keys_dict = foreign_keys_dict
        return foreign_keys_dict

    def _get_foreign_key_for_column(self, column_name: str) -> str:
        """Return the ForeignKey string for a given column name."""
        foreign_key = self.foreign_keys_dict.get(column_name)
        if foreign_key:
            return f", {foreign_key}"
        return ""

            
    def generate(self) -> None:

        for table_name, info in self.metadata.items():
            self._get_foreign_keys(info.get("foreign_keys", []))
            print(f"foreign_keys_dict: {self.foreign_keys_dict}")
            rendered = self.template.render(
                table_name = table_name,
                class_name = snake_to_camel(table_name),
                columns = info.get("columns", []),
                sqlalchemy_imports = self._create_imports(info),
                map_pg_type_to_sqlalchemy = map_pg_type_to_sqlalchemy,
                get_foreign_key_for_column = self._get_foreign_key_for_column
            )

            output_path = os.path.join(self.output_dir, f"{table_name}.py")
            with open(output_path, "w") as f:
                f.write(rendered)