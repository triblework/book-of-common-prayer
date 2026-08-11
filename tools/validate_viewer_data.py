#!/usr/bin/env python3
"""Validate emitted viewer JSON against the JSON Schemas (spec §3.5, §14 step 5).

Hard gate for CI, independent of the builder: every ``viewer/data/*.json`` is
validated against ``index.schema.json`` / ``service.schema.json`` (draft 2020-12).
Prefers the reference ``jsonschema`` package; falls back to the builder's built-in
stdlib validator so this still runs with no third-party dependency.

Usage:
    python tools/validate_viewer_data.py [DATA_DIR] [SCHEMA_DIR]
Defaults: DATA_DIR=viewer/data, SCHEMA_DIR=<DATA_DIR>/schema
"""

import json
import os
import sys


def main(argv):
    data_dir = argv[1] if len(argv) > 1 else "viewer/data"
    schema_dir = argv[2] if len(argv) > 2 else os.path.join(data_dir, "schema")

    with open(os.path.join(schema_dir, "index.schema.json"), encoding="utf-8") as fh:
        index_schema = json.load(fh)
    with open(os.path.join(schema_dir, "service.schema.json"), encoding="utf-8") as fh:
        service_schema = json.load(fh)

    try:
        import jsonschema
        engine = "jsonschema"

        def errors_for(obj, schema):
            v = jsonschema.Draft202012Validator(schema)
            return ["/".join(map(str, e.path)) + ": " + e.message for e in v.iter_errors(obj)]

        # Surface an invalid schema itself, not just invalid data.
        jsonschema.Draft202012Validator.check_schema(index_schema)
        jsonschema.Draft202012Validator.check_schema(service_schema)
    except ImportError:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from build_viewer_data import validate_against_schema
        engine = "builtin"

        def errors_for(obj, schema):
            return validate_against_schema(obj, schema)

    files = sorted(f for f in os.listdir(data_dir) if f.endswith(".json"))
    if not files:
        sys.stderr.write(f"no JSON files found in {data_dir}\n")
        return 2

    failures = 0
    for name in files:
        with open(os.path.join(data_dir, name), encoding="utf-8") as fh:
            obj = json.load(fh)
        schema = index_schema if name == "index.json" else service_schema
        errs = errors_for(obj, schema)
        if errs:
            failures += 1
            sys.stderr.write(f"FAIL {name}:\n  " + "\n  ".join(errs[:25]) + "\n")

    if failures:
        sys.stderr.write(f"\nschema validation FAILED for {failures}/{len(files)} file(s)\n")
        return 1
    print(f"schema validation OK: {len(files)} files ({engine} validator)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
