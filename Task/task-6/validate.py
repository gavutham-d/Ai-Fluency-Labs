"""Validate model-generated arguments against the same schemas sent to the model."""
from tools import SCHEMAS


def validate_arguments(arguments, schema):
    """Return None if valid, otherwise explain the mismatch and expected inputs."""
    if not isinstance(arguments, dict):
        return "Arguments must be a JSON object; expected an object with the declared properties."

    properties = schema.get("properties", {})
    required = schema.get("required", [])
    missing = [name for name in required if name not in arguments]
    if missing:
        return f"Missing required argument(s): {', '.join(missing)}. Expected required fields: {', '.join(required)}."

    if schema.get("additionalProperties") is False:
        extra = [name for name in arguments if name not in properties]
        if extra:
            return f"Unexpected argument(s): {', '.join(extra)}. Expected only: {', '.join(properties)}."

    for name, value in arguments.items():
        if name not in properties:
            continue
        rule = properties[name]
        expected_type = rule.get("type")
        type_ok = {
            "string": lambda item: isinstance(item, str),
            "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
            "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
            "boolean": lambda item: isinstance(item, bool),
            "object": lambda item: isinstance(item, dict),
            "array": lambda item: isinstance(item, list),
        }.get(expected_type, lambda item: True)
        if not type_ok(value):
            return f"Argument '{name}' has wrong type: expected {expected_type}, got {type(value).__name__}."
        if "enum" in rule and value not in rule["enum"]:
            return f"Argument '{name}' must be one of {rule['enum']}; expected a listed value, got {value!r}."
        if expected_type in ("number", "integer"):
            if "minimum" in rule and value < rule["minimum"]:
                return f"Argument '{name}' must be at least {rule['minimum']}; got {value}."
            if "maximum" in rule and value > rule["maximum"]:
                return f"Argument '{name}' must be at most {rule['maximum']}; got {value}."

    return None


if __name__ == "__main__":
    for tool_name, schema in SCHEMAS.items():
        required_values = {"plant": "basil"}
        if "season" in schema["properties"]:
            required_values["season"] = "summer"
        else:
            required_values["pot_size_liters"] = 2.0
        print(tool_name, "valid ->", validate_arguments(required_values, schema))
