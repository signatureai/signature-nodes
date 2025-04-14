import os
import shutil
import subprocess  # nosec B404
from pathlib import Path


def get_version() -> str:
    """Get the current version from environment or git tags."""
    # First check for version in environment variable
    if version := os.environ.get("PACKAGE_VERSION"):
        return version.lstrip("v")  # Remove 'v' prefix if present

    # Fall back to git tag version
    try:
        git_path = shutil.which("git")
        if not git_path:
            return "0.0.0"

        git_cmd = Path(git_path)
        if not git_cmd.exists():
            return "0.0.0"

        if not str(git_cmd).startswith(("/usr/bin", "/usr/local/bin", "/bin")):
            return "0.0.0"

        result = subprocess.run(  # nosec B404 B603
            [str(git_cmd), "describe", "--tags", "--match", "v*", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
            shell=False,
        )
        return result.stdout.strip().lstrip("v")  # Remove 'v' prefix
    except (subprocess.SubprocessError, OSError):
        return "0.0.0"


__version__ = get_version()
