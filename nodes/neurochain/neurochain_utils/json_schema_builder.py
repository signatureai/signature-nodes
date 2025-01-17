import json

from ...categories import NEUROCHAIN_UTILS_CAT


class JsonSchemaBuilder:
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "num_fields": ([str(i) for i in range(1, 11)], {"default": "1"}),
            },
            "optional": {},
        }

        for i in range(1, 11):
            inputs["optional"].update(
                {
                    f"field_name_{i}": ("STRING", {}),
                    f"field_type_{i}": (["string", "float", "integer", "boolean"], {"default": "string"}),
                    f"field_description_{i}": ("STRING", {}),
                    f"field_required_{i}": ("BOOLEAN", {"default": True}),
                }
            )
        return inputs

    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"
    CLASS_ID = "json_schema_builder"
    CATEGORY = NEUROCHAIN_UTILS_CAT

    def execute(self, **kwargs):
        field_type_map = {"string": "string", "float": "number", "integer": "integer", "boolean": "boolean"}
        num_fields = int(kwargs.get("num_fields", 1))
        fields = []
        for i in range(1, num_fields + 1):
            field_name = kwargs.get(f"field_name_{i}")
            if not field_name:
                raise ValueError(f"Field name is required for field {i}")
            field_type = kwargs.get(f"field_type_{i}")
            if not field_type:
                raise ValueError(f"Field type is required for field {i}")
            field_description = kwargs.get(f"field_description_{i}")
            field_required = kwargs.get(f"field_required_{i}")
            fields.append(
                {
                    "name": field_name,
                    "type": field_type_map[field_type],
                    "description": field_description,
                    "required": field_required,
                }
            )

        properties = {}
        for field in fields:
            properties[field["name"]] = {"type": field["type"]}
            if field["description"]:
                properties[field["name"]]["description"] = field["description"]

        schema = {
            "type": "object",
            "properties": properties,
            "required": [field["name"] for field in fields if field["required"]],
        }

        return (json.dumps(schema, indent=2),)
