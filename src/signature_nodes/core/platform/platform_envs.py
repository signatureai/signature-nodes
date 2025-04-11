import os

from ...categories import PLATFORM_IO_CAT


class PlatformEnvs:
    @classmethod
    def INPUT_TYPES(cls):  # type: ignore
        return {
            "required": {
                "environment": (["production", "staging", "develop"],),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
    )
    RETURN_NAMES = (
        "ORG_ID",
        "ORG_TOKEN",
    )
    FUNCTION = "execute"
    CATEGORY = PLATFORM_IO_CAT
    DESCRIPTION = """Retrieves organization ID and token based on the specified environment."""

    def execute(self, **kwargs):
        env = kwargs.get("environment") or ""
        org_id = "ORG_ID" if env == "production" else f"{env.upper()}_ORG_ID"
        org_token = "ORG_TOKEN" if env == "production" else f"{env.upper()}_ORG_TOKEN"
        ORG_ID = os.environ.get(org_id)
        ORG_TOKEN = os.environ.get(org_token)
        return (
            ORG_ID,
            ORG_TOKEN,
        )
