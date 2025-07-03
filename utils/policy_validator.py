from jsonschema import validate, ValidationError

TRUST_POLICY_SCHEMA = {
    "type": "object",
    "properties": {
        "rules": {
            "type": "object",
            "patternProperties": {
                "^.*$": {  # ✅ Accept any rule name
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "weight": {"type": "number"}
                    },
                    "required": ["enabled", "weight"],
                    "additionalProperties": True  # allow rule-specific extras like "threshold", "hours", etc.
                }
            },
            "additionalProperties": False  # disallow rule names outside pattern
        },
        "final_threshold": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        }
    },
    "required": ["rules", "final_threshold"],
    "additionalProperties": False
}

def validate_trust_policy(json_data):
    validate(instance=json_data, schema=TRUST_POLICY_SCHEMA)
