from jsonschema import validate, ValidationError

TRUST_POLICY_SCHEMA = {
    "type": "object",
    "properties": {
        "rules": {
            "type": "object",
            "properties": {
                "large_transaction": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "weight": {"type": "number"},
                        "threshold": {"type": "number"}
                    },
                    "required": ["enabled", "weight"]
                },
                "odd_hours": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "weight": {"type": "number"},
                        "hours": {
                            "type": "array",
                            "items": {"type": "integer", "minimum": 0, "maximum": 23}
                        }
                    },
                    "required": ["enabled", "weight"]
                },
                "new_device_or_ip": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "weight": {"type": "number"}
                    },
                    "required": ["enabled", "weight"]
                },
                "geo_trust": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "weight": {"type": "number"},
                        "min_trust_score": {"type": "number"}
                    },
                    "required": ["enabled", "weight"]
                }
            },
            "additionalProperties": False
        },
        "final_threshold": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "required": ["rules", "final_threshold"],
    "additionalProperties": False
}

def validate_trust_policy(json_data):
    validate(instance=json_data, schema=TRUST_POLICY_SCHEMA)
