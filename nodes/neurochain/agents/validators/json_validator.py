import json

from jsonschema import validate

from ....categories import AGENT_RESPONSE_VALIDATORS_CAT


class JSONValidator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_schema": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("FUNCTION", "STRING")
    RETURN_NAMES = ("validator", "support_directives")
    FUNCTION = "process"
    CATEGORY = AGENT_RESPONSE_VALIDATORS_CAT
    OUTPUT_NODE = True

    def process(self, json_schema: str):
        json_schema_str = json_schema.replace("{", "{{")
        json_schema_str = json_schema_str.replace("}", "}}")

        support_directives = "Structure the output as a valid JSON\n"
        support_directives += "The JSON should respect the following JSON-SCHEMA:\n"
        support_directives += json_schema_str + "\n"

        schema = json.loads(json_schema)

        def validate_json(text: str):
            try:
                json_dict = json.loads(text)
                validate(instance=json_dict, schema=schema)
                return True
            except:
                return False

        return (validate_json, support_directives)
