import os
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv


class Environment:
    _instance = None
    _initialized = False

    # Format: (name, required, default_value, allowed_values)
    ENV_VARS: list[Tuple[str, bool, Any, Optional[list[Any]]]] = [
        ("WEBSERVICE_URL", False, None, None),
        ("OPENAI_API_KEY", False, None, None),
        ("WEAVIATE_URL", False, None, None),
        ("BACKEND_COGNITO_SECRET", True, None, None),
        ("ENVIRONMENT", True, "staging", ["staging", "production"]),
        ("JENKINS_URL", True, None, None),
        ("JENKINS_AUTH", True, None, None),
        ("PARALLEL_PROCESSING", False, "False", ["True", "False"]),
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            load_dotenv()
            self._env_values: Dict[str, Any] = {}
            self._load_env_vars()
            self._initialized = True

    def _load_env_vars(self) -> None:
        """Load all environment variables defined in ENV_VARS."""
        for name, required, default, allowed_values in self.ENV_VARS:
            value = os.getenv(name)

            if value is None:
                if required:
                    raise ValueError(f"{name} environment variable is not set")
                value = default
            else:
                if allowed_values is not None and value not in allowed_values:
                    raise ValueError(f"{name} environment variable has an invalid value: {value}")

            self._env_values[name] = value

    def get(self, name: str) -> Any:
        """Get an environment variable by name."""
        if name not in self._env_values:
            raise KeyError(f"Environment variable '{name}' is not defined in ENV_VARS")
        return self._env_values[name]

    def __str__(self) -> str:
        return str(self._env_values)


env = Environment()
