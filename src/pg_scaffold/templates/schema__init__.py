import inspect
import pkgutil
import importlib
from pathlib import Path
from pydantic import BaseModel



__all__ = []

# Dynamically import all modules in this package
package_dir = Path(__file__).parent
for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
    importlib.import_module(f"{__package__}.{module_name}")


# 1. Collect all schemas
schemas = {}
for name, obj in list(globals().items()):
    if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
        __all__.append(name)
        schemas[name] = obj


# 2. Separate schemas into two collections
relationship_schemas = {name: schema for name, schema in schemas.items() if "With" in name}
no_relationship_schemas = {name: schema for name, schema in schemas.items() if "With" not in name}

# 3. Create complete ordered list: no relationships first, then relationships
rebuild_order = list(no_relationship_schemas.keys()) + list(relationship_schemas.keys())

# Rebuild schemas in dependency order
for schema_name in rebuild_order:
    try:
        schemas[schema_name].model_rebuild()
        print(f"✅ Rebuilt schema: {schema_name}")
    except Exception as e:
        print(f"⚠️ Failed to rebuild schema {schema_name}: {e}")

# 4. Sort __all__ for clean, consistent imports
__all__.sort()

print(f"📦 Loaded {len(__all__)} schemas: {', '.join(__all__)}")
