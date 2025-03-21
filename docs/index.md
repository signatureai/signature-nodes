# Signature Nodes Documentation

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


# **Working with AWS CodeArtifact**
The process is documented on [his Notion page](https://www.notion.so/ML-Team-Setup-Ways-of-Working-134dce05f47a800d99ebe36e36a1da85?pvs=4#196dce05f47a80128633e9783c20da9a).

# **Git Flow Usage Guide**

[[Setup Reference](https://skoch.github.io/Git-Workflow/)]  [[Usage Reference](https://skoch.github.io/Git-Workflow/with-gitflow.html)]

Git Flow is a branching model that helps teams manage feature development, releases, and hotfixes in a systematic way.

## **Installation**

### **OSX (Homebrew)**

```markdown
brew install git-flow
```

## **Initial Setup**

### **Initialize Repository**

```markdown
cd my/project
git commit -am "Initial commit"
git remote add origin git@github.com:username/Project-Name.git
git push -u origin main
```

### **Prepare for Development**

```markdown
git checkout -b develop
git push -u origin develop
```

- **Important:** Set the default branch to `develop` on GitHub!

### **Initialize Git Flow**

Run the initialization command:

```markdown
git flow init [-d]
```

Use `-d` flag to accept all defaults, or configure the following settings:

- Production branch: [`main`]
- Development branch: [`develop`]
- Feature prefix: [`feature/`]
- Release prefix: [`release/`]
- Hotfix prefix: [`hotfix/`]
- Support prefix: [`support/`]
- Version tag prefix: []

## **Working with Features**

### **Start a New Feature**

```markdown
git flow feature start ML-123-my-feature
```

This creates a new branch `feature/ML-123-my-feature` based on `develop`.

### **Complete a Feature**

```markdown
git flow feature finish ML-123-my-feature
```

This action:

- Merges `feature/ML-123-my-feature` into `develop`
- Removes the feature branch
- Switches back to `develop`

## **Creating Releases**

### **Start a Release**

```markdown
git fetch --tags  # Check existing tags first
git flow release start 1.0
```

### **During Release**

1. Update version numbers in documentation

2. Make final adjustments (no new features!)

3. Commit changes:

```markdown
git commit -am "Bumped version number to 1.0"
```

### **Finish Release**

```markdown
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

## **Handling Hotfixes**

### **Start a Hotfix**

```markdown
git flow hotfix start 1.0.1
```

### **During Hotfix**

1. Update version numbers

2. Fix the critical bug

3. Commit changes:

```markdown
git commit -am "Fixed critical bug"
```

### **Finish Hotfix**

```markdown
git flow hotfix finish 1.0.1
git push origin main
git push origin develop
git push --tags
```

This action:

- Merges hotfix into both `main` and `develop`
- Tags the new version
- Removes the hotfix branch

## **Best Practices**

1. Keep feature branches focused and short-lived

2. Only bug fixes in release branches

3. Use hotfixes only for critical production issues

4. Always push your changes to remote after finishing features/releases/hotfixes
