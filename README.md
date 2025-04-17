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

## Working with AWS CodeArtifact

The process is documented on [this Notion page](https://www.notion.so/ML-Team-Setup-Ways-of-Working-134dce05f47a800d99ebe36e36a1da85?pvs=4#196dce05f47a80128633e9783c20da9a).

## Git Flow Usage Guide

This process is documented on [this Notion page](https://www.notion.so/ML-Team-Onboarding-Ways-of-Working-134dce05f47a800d99ebe36e36a1da85#197dce05f47a8092b695f4ebce0da839)
