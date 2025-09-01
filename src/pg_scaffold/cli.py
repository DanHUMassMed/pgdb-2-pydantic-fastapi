import argparse
import os
import sys
import json
import shutil
import importlib

from pg_scaffold.generator.inspector import DatabaseInspector
from pg_scaffold.preserve_custom.preservation import CodePreservationManager
from pg_scaffold.generator.utils import get_templates_dir


class FriendlyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        print(f"\n❌ ERROR: {message}\n", file=sys.stderr)
        print("💡 Example usage:", file=sys.stderr)
        print("   python -m pg_scaffold --pgdb postgresql://user:pass@localhost/db --output ./out --version v1\n", file=sys.stderr)
        sys.exit(2)


def load_generators(version: str):
    try:
        model_module = importlib.import_module(f"pg_scaffold.generator.{version}.model_generator")
        schema_module = importlib.import_module(f"pg_scaffold.generator.{version}.schema_generator")
        crud_module = importlib.import_module(f"pg_scaffold.generator.{version}.crud_generator")
        api_module = importlib.import_module(f"pg_scaffold.generator.{version}.api_generator")
        main_module = importlib.import_module(f"pg_scaffold.generator.{version}.main_generator")

        return {
            "ModelGenerator": model_module.ModelGenerator,
            "SchemaGenerator": schema_module.SchemaGenerator,
            "CRUDGenerator": crud_module.CRUDGenerator,
            "APIGenerator": api_module.APIGenerator,
            "MainGenerator": main_module.MainGenerator,
        }
    except ModuleNotFoundError as e:
        print(f"❌ ERROR: Generator version '{version}' not found ({e}).\n")
        sys.exit(1)

def main():
    parser = FriendlyArgumentParser(description="Generate a FastAPI app scaffold from a PostgreSQL database.")
    parser.add_argument("--pgdb", required=False, help="PostgreSQL connection string (e.g., postgresql://user:pass@localhost/db)")
    parser.add_argument("--output_dir", required=True, help="Output directory to save the generated FastAPI app")
    parser.add_argument("--sql_json_dir", required=False, help="Input directory containing SQL JSON files to use for model generation")
    parser.add_argument("--version", required=False, default="v2", help="Generator version to use (e.g., v1, v2)")

    args = parser.parse_args()

    print(f"=== Running code generation with:\n\tDB:{args.pgdb}\n\tOutput Dir:{args.output_dir}\n\tVersion:{args.version}")
    app_dir = os.path.join(args.output_dir, "app")

    if args.sql_json_dir is None:
        args.sql_json_dir = os.path.join(args.output_dir, "schema_json")

    # Step 1: Inspect database
    if args.pgdb:
        inspector = DatabaseInspector(args.pgdb, args.output_dir)
        inspector.generate_scheme_json()

    manager = CodePreservationManager(app_dir)
    preserved_code = manager.preserve_custom_code()

    # Load generators dynamically
    generators = load_generators(args.version)

    # Step 2: Generate models
    generators["ModelGenerator"](args.sql_json_dir, app_dir, args.version).generate()

    # Step 3: Generate schemas
    generators["SchemaGenerator"](args.sql_json_dir, app_dir, args.version).generate()

    # Step 4: Generate CRUD operations
    generators["CRUDGenerator"](args.sql_json_dir, app_dir, args.version).generate()

    # Step 5: Generate API endpoints
    generators["APIGenerator"](args.sql_json_dir, app_dir, args.version).generate()

    # Step 6: Generate main application file
    generators["MainGenerator"](args.sql_json_dir, app_dir, args.version).generate()

    # Copy helper files
    src = os.path.join(get_templates_dir(args.version), "run_app.sh")
    dst = os.path.join(args.output_dir, "run_app.sh")
    shutil.copy(src, dst)

    src = os.path.join(get_templates_dir(args.version), "env")
    dst = os.path.join(args.output_dir, ".env")
    if not os.path.exists(dst):
        shutil.copy(src, dst)

    manager.set_target_directory(app_dir)
    manager.restore_custom_code(preserved_code)


if __name__ == "__main__":
    main()