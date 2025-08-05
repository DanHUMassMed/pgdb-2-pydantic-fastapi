import os
import json
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.reflection import Inspector

class GeneratorBase:
    def __init__(self, pgdb_url: str, output_path: str):
        self.pgdb_url = pgdb_url
        self.output_path = output_path

    def _map_column_type(self, col_type):
        # Use the type's class name as a string (e.g., Integer, String)
        return col_type.__class__.__name__

    def inspect_database(self):
        engine = create_engine(self.pgdb_url)
        inspector: Inspector = inspect(engine)

        os.makedirs(self.output_path, exist_ok=True)

        for table_name in inspector.get_table_names():
            # Capitalize class name from table name (e.g., attendees -> Attendee)
            model_name = table_name.capitalize()

            imports = set()
            fields = []
            relationships = []

            for column in inspector.get_columns(table_name):
                name = column["name"]
                col_type = self._map_column_type(column["type"])
                imports.add(col_type)

                args = []
                if column.get("primary_key"):
                    args.append("primary_key=True")
                if column.get("nullable") is False:
                    args.append("nullable=False")
                if column.get("default") is not None:
                    args.append(f'default={repr(column["default"])}')
                if column.get("index"):
                    args.append("index=True")

                # Foreign key check
                fks = inspector.get_foreign_keys(table_name)
                fk_str = ""
                for fk in fks:
                    if name in fk["constrained_columns"]:
                        ref_table = fk["referred_table"]
                        ref_column = fk["referred_columns"][0]
                        fk_str = f'ForeignKey("{ref_table}.{ref_column}")'
                        imports.add("ForeignKey")
                        args.append(fk_str)
                        relationships.append({
                            "name": ref_table.rstrip("s"),  # naive singular
                            "related_model": ref_table.capitalize()
                        })

                fields.append({
                    "name": name,
                    "type": col_type,
                    "args": ", ".join(args)
                })

            model_def = {
                "model_name": model_name,
                "table_name": table_name,
                "imports": sorted(imports),
                "fields": fields,
                "relationships": relationships
            }

            output_file = os.path.join(self.output_path, f"{table_name}.json")
            with open(output_file, "w") as f:
                json.dump(model_def, f, indent=2)

            print(f"✅ JSON schema written: {output_file}")