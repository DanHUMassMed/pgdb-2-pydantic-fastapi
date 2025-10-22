import argparse
import os
import sys
import json
import shutil
import importlib

from pg_scaffold.generator.inspector import DatabaseInspector
from pg_scaffold.preserve_custom.preservation import CodePreservationManager
from pg_scaffold.generator.utils import get_templates_dir

# Define generator execution order
GENERATOR_ORDER = [
    "ModelGenerator",
    "SchemaGenerator",
    "CRUDGenerator",
    "APIGenerator",
    "MainGenerator",
    "HelperGenerator",
    "TypescriptGenerator",
]
class FriendlyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        print(f"\n❌ ERROR: {message}\n", file=sys.stderr)
        print("💡 Example usage:", file=sys.stderr)
        print("   python -m pg_scaffold --pgdb postgresql://user:pass@localhost/db --output ./out --version v1\n", file=sys.stderr)
        sys.exit(2)

def load_generators(version: str):
    modules = {
        "ModelGenerator": f"pg_scaffold.generator.{version}.model_generator",
        "SchemaGenerator": f"pg_scaffold.generator.{version}.schema_generator",
        "CRUDGenerator": f"pg_scaffold.generator.{version}.crud_generator",
        "APIGenerator": f"pg_scaffold.generator.{version}.api_generator",
        "MainGenerator": f"pg_scaffold.generator.{version}.main_generator",
        "HelperGenerator": f"pg_scaffold.generator.{version}.helper_generator",
        "TypescriptGenerator": f"pg_scaffold.generator.{version}.typescript_generator",
    }

    loaded = {}

    for name, path in modules.items():
        try:
            module = importlib.import_module(path)
            loaded[name] = getattr(module, name)
        except ModuleNotFoundError:
            print(f"⚠️  WARNING: {name} not found for version '{version}', skipping.")
        except AttributeError:
            print(f"⚠️  WARNING: {name} class missing in {path}, skipping.")

    if not loaded:
        print(f"❌ ERROR: No generators could be loaded for version '{version}'.")
        sys.exit(1)

    return loaded


def run_generators(generators: dict, args):
    output_dir = os.path.join(args.output_dir)

    for name in GENERATOR_ORDER:
        gen_class = generators.get(name)
        if not gen_class:
            print(f"⚠️  Skipping {name}, not loaded.")
            continue

        print(f"✅ Running {name}...")

        instance = gen_class(args.sql_json_dir, output_dir, args.version)
        instance.generate()


def main():
    parser = FriendlyArgumentParser(description="Generate a FastAPI app scaffold from a PostgreSQL database.")
    parser.add_argument("--pgdb", required=False, help="PostgreSQL connection string (e.g., postgresql://user:pass@localhost/db)")
    parser.add_argument("--output_dir", required=True, help="Output directory to save the generated FastAPI app")
    parser.add_argument("--sql_json_dir", required=False, help="Input directory containing SQL JSON files to use for model generation")
    parser.add_argument("--version", required=False, default="v2", help="Generator version to use (e.g., v1, v2)")

    args = parser.parse_args()

    print(f"=== Running code generation with:\n\tDB:{args.pgdb}\n\tOutput Dir:{args.output_dir}\n\tVersion:{args.version}")
    output_dir = os.path.join(args.output_dir)
    app_dir = os.path.join(args.output_dir, "app")

    if args.sql_json_dir is None:
        args.sql_json_dir = os.path.join(args.output_dir, "schema_json")

    # Inspect database
    if args.pgdb:
        inspector = DatabaseInspector(args.pgdb, args.output_dir)
        inspector.generate_scheme_json()

    manager = CodePreservationManager(output_dir)
    preserved_code = manager.preserve_custom_code()

    generators = load_generators(args.version)

    run_generators(generators, args)

    manager.set_target_directory(output_dir)
    manager.restore_custom_code(preserved_code)


if __name__ == "__main__":
    main()