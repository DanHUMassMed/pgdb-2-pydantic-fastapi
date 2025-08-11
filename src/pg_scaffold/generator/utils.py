# app/generator/utils.py
import os
from typing import Optional
import inflect

inflector = inflect.engine()

def is_plural(word):
    return inflector.singular_noun(word) is not False

def singular(word):
    if is_plural(word):
        return inflector.singular_noun(word)
    return word

def plural(word):
    if is_plural(word):
        return word
    return inflector.plural(word)


def snake_to_pascal(snake_str: str) -> str:
        return ''.join(word.capitalize() for word in snake_str.split('_'))
    
def table_name_to_class_name(table_name: str) -> str:
    parts: list[str] = table_name.split('_')

    if parts:
        last_word = singular(parts[-1])
        parts[-1] = last_word # type: ignore

    return ''.join(word.capitalize() for word in parts)

def table_name_to_file_name(table_name: str) -> str:
    parts: list[str] = table_name.split('_')

    if parts:
        last_word = singular(parts[-1])
        parts[-1] = last_word # type: ignore

    return '_'.join(parts)

def table_name_to_variable_name(table_name: str, use_singular: bool) -> str:
    parts: list[str] = table_name.split('_')
    if parts and use_singular:
        parts[-1] = singular(parts[-1])

    return '_'.join(parts)  # keeps variable_name format

def map_pg_type_to_sqlalchemy_type(pg_type: str) -> str:
    """Map PostgreSQL type to SQLAlchemy type."""
    mapping = {
        "INTEGER": "Integer",
        "TEXT": "String",
        "VARCHAR": "String",
        "TIMESTAMP": "TIMESTAMP",
        "BOOLEAN": "Boolean",
        "FLOAT": "Float",
        "DATE": "Date",
        "UUID": "UUID",
    }
    return mapping.get(pg_type.upper(), "String")  # default fallback

def map_pg_column_to_sqlalchemy(pg_col: dict, optional:bool = False) -> str:
    """Map PostgreSQL type to SQLAlchemy type."""
    pg_type = pg_col.get("type", "TEXT")
    server_default = pg_col.get("server_default", False)
    primary_key = pg_col.get("primary_key", False)
    optional = optional or server_default
    optional = optional and not primary_key
    mapping = {
        "INTEGER": "int",
        "TEXT": "str",
        "VARCHAR": "str",
        "TIMESTAMP": "datetime",
        "BOOLEAN": "bool",
        "FLOAT": "float",
        "DATE": "date",
        "UUID": "UUID",
    }
    data_type = mapping.get(pg_type.upper(), "str")  # default fallback
    
    return  f"{data_type} | None" if optional else data_type


def map_pg_column_to_python(pg_col: dict, optional:bool = False) -> str:
    """Map PostgreSQL type to python type."""
    pg_type = pg_col.get("type", "TEXT")
    server_default = pg_col.get("server_default", False)
    mapping = {
        "INTEGER": "int",
        "TEXT": "str",
        "VARCHAR": "str",
        "TIMESTAMP": "datetime",
        "BOOLEAN": "bool",
        "FLOAT": "float",
        "DATE": "date",
        "UUID": "UUID",
    }
    data_type = mapping.get(pg_type.upper(), "str")  # default fallback
    
    return  f"Optional[{data_type}] = None" if optional or server_default else data_type


def ensure_package_dirs(path: str):
    """
    Ensures that `path` and all parent directories up to the first
    directory in the relative path contain an __init__.py file.
    """
    if os.path.isabs(path):
        raise ValueError(f"`path` must be relative, got absolute path: {path}")

    # Normalize path to remove trailing slashes, resolve '.' or '..'
    path = os.path.normpath(path)

    # Extract the first part of the path — the top-level directory
    parts = path.split(os.sep)
    if len(parts) == 1:
        stop_at = path  # e.g., just "app"
    else:
        stop_at = parts[0]  # e.g., "app" from "app/models/schema"

    # Ensure full target directory exists
    os.makedirs(path, exist_ok=True)

    current = path
    while True:
        # Create __init__.py if missing
        init_path = os.path.join(current, "__init__.py")
        os.makedirs(current, exist_ok=True)
        if not os.path.exists(init_path):
            with open(init_path, "a"):
                os.utime(init_path, None)

        if current == stop_at:
            break

        parent = os.path.dirname(current)
        if parent == current:
            break  # reached '.'

        current = parent