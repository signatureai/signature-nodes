# Signature for ComfyUI

![GitHub](https://img.shields.io/github/license/signatureai/signature-nodes)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?&logo=PyTorch&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?&logo=numpy&logoColor=white)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?&logo=opencv&logoColor=white)
![ComfyUI](https://img.shields.io/badge/ComfyUI-compatible-green)

A powerful collection of custom nodes for ComfyUI that provides essential image
processing, data handling, and workflow management capabilities.

📚 **[View Full Documentation](https://signatureai.github.io/signature-nodes/)**

## 🚀 Installation

1. Navigate to your ComfyUI custom nodes directory:

```bash
cd ComfyUI/custom_nodes/
```

2. Clone the repository:

```bash
git clone https://github.com/signatureai/signature-nodes.git
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## 📦 Node Categories

- ⚡ Basic
  - 🧱 Primitives - Basic data type nodes
  - 🔢 Numbers - Numerical operations and processing
  - 🔤 Text - Text processing and manipulation nodes
  - 📁 File - File handling operations
  - 🖼️ Image - Basic image handling nodes
  - 🎭 Mask - Mask generation and operations
- 🖼️ Image Processing - Advanced image processing and manipulation nodes
- 🤖 Models - AI model integration nodes
- 🧠 Logic - Logic operations and control flow
- 🛠️ Utils - Utility functions
- 📦 Others
  - 🔀 Augmentations - Image augmentation tools
  - 🔌 Platform I/O - Platform integration nodes
  - 📊 Data - Data conversion and handling
  - 🧬 Loras - LoRA model handling and integration

## 💻 Usage

After installation, the Signature nodes will be available in your ComfyUI workspace
under the "🔲 Signature Nodes" category. Each node is designed to be intuitive and
includes proper input validation and error handling.

### Example Workflow

1. Load an image using `ImageFromWeb` or `ImageFromBase64`
2. Apply transformations using nodes like `ImageTranspose` or `UpscaleImage`
3. Process the image using various filter nodes
4. Export the result using `PlatformOutput` or save directly

## 📁 Project Structure

- `nodes/` - Node implementations
  - `web/` - Web interface components
  - `categories.py` - Node category definitions
  - `shared.py` - Shared utilities and constants
  - `platform_io.py` - Platform integration
  - `wrapper.py` - Workflow wrapper functionality
- `docs/` - Documentation files
- `scripts/` - Development and build scripts

## 🛠 Development Setup

1. Install uv if not already installed:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install the python environment:

```shell
uv sync
```

3. Install the pre-commit hooks for checks and file format fixed (after doing this, git will "remember" that this uv
   environment is the python environment which should be used to run the pre-commit hooks):

```shell
uv run pre-commit install
```

4. Generate documentation:

```bash
uv run python scripts/generate_docs.py
```

## 📚 Documentation

Documentation is built using MkDocs with the Material theme. To view the documentation
locally:

1. Install MkDocs and dependencies:

```bash
uv sync --group doc
```

2. Serve the documentation:

```bash
uv run mkdocs serve
```

The documentation will be available at `http://localhost:8000`.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



# Git Flow Usage Guide

Git Flow is a branching model that helps teams manage feature development, releases, and hotfixes in a systematic way.

## Installation

### OSX (Homebrew)
```bash
brew install git-flow
```

## Initial Setup

### Initialize Repository
```bash
cd my/project
git commit -am "Initial commit"
git remote add origin git@github.com:username/Project-Name.git
git push -u origin main
```

### Prepare for Development
```bash
git checkout -b develop
git push -u origin develop
```

**Important:** Set the default branch to `develop` on GitHub!

### Initialize Git Flow
Run the initialization command:
```bash
git flow init [-d]
```

Use `-d` flag to accept all defaults, or configure the following settings:
- Production branch: [main]
- Development branch: [develop]
- Feature prefix: [feature/]
- Release prefix: [release/]
- Hotfix prefix: [hotfix/]
- Support prefix: [support/]
- Version tag prefix: []

## Working with Features

### Start a New Feature
```bash
git flow feature start my-feature
```
This creates a new branch `feature/my-feature` based on `develop`.

### Complete a Feature
```bash
git flow feature finish my-feature
```
This action:
- Merges `feature/my-feature` into `develop`
- Removes the feature branch
- Switches back to `develop`

## Creating Releases

### Start a Release
```bash
git fetch --tags  # Check existing tags first
git flow release start 1.0
```

### During Release
1. Update version numbers in documentation
2. Make final adjustments (no new features!)
3. Commit changes:
```bash
git commit -am "Bumped version number to 1.0"
```

### Finish Release
```bash
git flow release finish 1.0
git push origin main
git push origin develop
git push --tags
```

This action:
- Merges release into `main`
- Tags the release
- Back-merges into `develop`
- Removes the release branch

## Handling Hotfixes

### Start a Hotfix
```bash
git flow hotfix start 1.0.1
```

### During Hotfix
1. Update version numbers
2. Fix the critical bug
3. Commit changes:
```bash
git commit -am "Fixed critical bug"
```

### Finish Hotfix
```bash
git flow hotfix finish 1.0.1
git push origin main
git push origin develop
git push --tags
```

This action:
- Merges hotfix into both `main` and `develop`
- Tags the new version
- Removes the hotfix branch

## Best Practices

1. Keep feature branches focused and short-lived
2. Only bug fixes in release branches
3. Use hotfixes only for critical production issues
4. Always push your changes to remote after finishing features/releases/hotfixes


# UV Package Manager with AWS CodeArtifact

This guide explains how to use UV package manager with AWS CodeArtifact for Python package management.

## Prerequisites

- AWS CLI installed and configured
- UV package manager installed
- Appropriate AWS IAM permissions for CodeArtifact access

## AWS Credentials Setup

1. Configure your AWS credentials:
```bash
aws configure
```

2. Set required environment variables:
```bash
export AWS_PROFILE=your-profile-name  # If using named profiles
export AWS_REGION=${AWS_REGION}          # Your AWS region
```

## AWS CodeArtifact Authentication

Make sure you have you `.env` file at the root of your project.

a `Makefile` has been added to easily generate tokens and create an environment:

Generate a remote repository token:
```
make token
```

Create a virtual environment with `uv sync`:
```
make setup
```

Generate an authentication token for CodeArtifact:

When pushing packages to AWS CodeArtifact we first need to login using this command:

```bash
aws codeartifact login --tool pip --domain ${EXTRA_INDEX_DOMAIN} --repository ${EXTRA_INDEX_REPO} --region ${AWS_REGION}
```

When installing Signature packages from our AWS CodeArtifact repository we need to create a [uv-compatible environment variable](https://docs.astral.sh/uv/configuration/indexes/#providing-credentials) with an AWS CodeArtifact token:

```bash
export UV_INDEX_SIGNATURE_PASSWORD="$(
    aws codeartifact get-authorization-token \
    --domain ${EXTRA_INDEX_DOMAIN} \
    --domain-owner ${AWS_ACCOUNT_ID} \
    --query authorizationToken \
    --output text
)"
```
**Note:** This token expires after 12 hours


## Configuring UV with CodeArtifact

### Setup in pyproject.toml

1. Define the CodeArtifact index:
```toml
[[tool.uv.index]]
name = "signature"
url = "https://${EXTRA_INDEX_DOMAIN}-${AWS_ACCOUNT_ID}.d.codeartifact.${AWS_REGION}.amazonaws.com/pypi/${EXTRA_INDEX_REPO}/simple/"
explicit = true
```

2. Pin private packages to the CodeArtifact index:
```toml
[tool.uv.sources]
neurochain = { index = "signature" }
signature-core = { index = "signature" }
signature-flows = { index = "signature" }
```

**Note**: Setting `explicit = true` means packages will only be installed from CodeArtifact when explicitly pinned to it.

### Authentication

Before running UV commands, set up authentication:

```bash
export UV_INDEX_SIGNATURE_PASSWORD="$(
    aws codeartifact get-authorization-token \
    --domain ${EXTRA_INDEX_DOMAIN} \
    --domain-owner ${AWS_ACCOUNT_ID} \
    --query authorizationToken \
    --output text
)"
```

### Installing or Updating Packages

After setting the authentication token:

1. Install all dependencies:
```bash
uv sync
```

2. Add or update a specific package:
```bash
uv add neurochain==2.0.0
```
The package will automatically use the correct index based on the `tool.uv.sources` configuration. Be sure to add the packages to the `tool.uv.sources` in the pyproject.toml file before installing it.


### Package Index Options

UV provides two different options for specifying package indexes:

1. `--index` - Persists to pyproject.toml:
```bash
# This will save the index URL to pyproject.toml
uv add neurochain --index https://aws:${UV_INDEX_SIGNATURE_PASSWORD}@${EXTRA_INDEX_DOMAIN}-${AWS_ACCOUNT_ID}.d.codeartifact.${AWS_REGION}.amazonaws.com/pypi/${EXTRA_INDEX_REPO}/simple/

```

2. `--index-url` - One-time use only:
```bash
# This will NOT save to pyproject.toml
uv add neurochain --extra-index-url https://aws:${UV_INDEX_SIGNATURE_PASSWORD}@${EXTRA_INDEX_DOMAIN}-${AWS_ACCOUNT_ID}.d.codeartifact.${AWS_REGION}.amazonaws.com/pypi/${EXTRA_INDEX_REPO}/simple/
```

**Note**: When using `--index`, multiple values are treated as additional indexes (similar to `--extra-index-url`).

### Installing Packages

Basic syntax:

Example:
```bash
uv add neurochain==2.0.0 --extra-index-url https://aws:${UV_INDEX_SIGNATURE_PASSWORD}@${EXTRA_INDEX_DOMAIN}-${AWS_ACCOUNT_ID}.d.codeartifact.${AWS_REGION}.amazonaws.com/pypi/${EXTRA_INDEX_REPO}/simple/
```


## Security Notes

1. Never commit CodeArtifact tokens to version control
2. Use environment variables or secure secrets management
3. Rotate AWS credentials regularly
4. Use minimum required IAM permissions
