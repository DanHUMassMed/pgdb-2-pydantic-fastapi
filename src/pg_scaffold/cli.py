import argparse
import os
import sys

import json

from pg_scaffold.generator.inspector import DatabaseInspector
from pg_scaffold.generator.model_generator import ModelGenerator
from pg_scaffold.generator.schema_generator import SchemaGenerator
from pg_scaffold.generator.crud_generator import CRUDGenerator
from pg_scaffold.generator.api_generator import APIGenerator
from pg_scaffold.generator.main_generator import MainGenerator

class FriendlyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        print(f"\n❌ ERROR: {message}\n", file=sys.stderr)
        print("💡 Example usage:", file=sys.stderr)
        print("   python -m pg_scaffold --pgdb postgresql://user:pass@localhost/db --output ./out\n", file=sys.stderr)
        sys.exit(2)

def main():
    parser = FriendlyArgumentParser(description="Generate a FastAPI app scaffold from a PostgreSQL database.")
    parser.add_argument("--pgdb", required=False, help="PostgreSQL connection string (e.g., postgresql://user:pass@localhost/db)")
    parser.add_argument("--output_dir", required=True, help="Output directory to save the generated FastAPI app")
    parser.add_argument("--sql_json_dir", required=False, help="Input directory containing SQL JSON files to use for model generation")

    args = parser.parse_args()

    # Set default for sql_json_dir if not provided
    if args.sql_json_dir is None:
        args.sql_json_dir = os.path.join(args.output_dir, "schema_json")
    
    # Step 1: Inspect database
    if args.pgdb:
        inspector = DatabaseInspector(args.pgdb, args.output_dir)
        inspector.generate_scheme_json()
    
    # Step 2: Generate models
    model_generator = ModelGenerator(args.sql_json_dir, args.output_dir)
    model_generator.generate()

    # Step 3: Generate schemas
    schema_generator = SchemaGenerator(args.sql_json_dir, args.output_dir)
    schema_generator.generate()
    
    # crud_generator = CRUDGenerator(args.sql_json_dir, args.output_dir)
    # crud_generator.generate()  
    
    # api_generator = APIGenerator(args.sql_json_dir, args.output_dir)
    # api_generator.generate()
    
    # main_generator = MainGenerator(args.sql_json_dir, args.output_dir)
    # main_generator.generate()
    
if __name__ == "__main__":
    main()