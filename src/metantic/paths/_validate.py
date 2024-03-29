from typing import Literal
import ramda as R

@R.curry
def ref(ref: str, defs: dict[str]) -> dict[str]:
    """`ref`: `'#/$defs/<key>'`"""
    key = ref.split('/')[-1]
    return defs[key]

def validate(path: list[str|int], schema: dict[str]) -> ValueError | None:
    """Validate `path` against `schema` as defined in the [JSON Schema](https://json-schema.org/learn/getting-started-step-by-step) spec
    - `schema` can be obtained via `BaseModel.model_json_schema()` ([pydantic docs](https://docs.pydantic.dev/latest/concepts/json_schema/))
    - Assumes `schema` is valid; otherwise an exception may be raised
    """
    def _validate(_schema: dict[str], _path: list[str]) -> ValueError | None:
        if _path == []:
            return None
        [k, *ks] = _path
        if '$ref' in _schema:
            sch = ref(_schema['$ref'], schema['$defs'])
            return _validate(sch, _path)
        if _schema.get("type") == "object":
            properties: dict[str] = _schema.get("properties", {})
            if k in properties:
                return _validate(properties[k], ks)
            else:
                return ValueError(f"Key '{k}' doesn't exist in {list(properties.keys())}")
        elif _schema.get("type") == "array" and str(k).isdigit():
            if 'items' in _schema:
                return _validate(_schema['items'], ks)
            elif 'prefixItems' in _schema:
                for option in _schema['prefixItems']:
                    val = _validate(option, ks)
                    if val is None:
                        return None
                return val
            else:
                raise NotImplementedError(f"Array type doesn't have 'items' nor 'prefixItems' keys. Schema: '{_schema}'")
        elif 'anyOf' in _schema:
            for option in _schema['anyOf']:
                val = _validate(option, _path)
                if val is None:
                    return None
            return val
        
        return ValueError(f"Key '{k}' doesn't exist in schema: '{_schema}'")
    return _validate(schema, path)