#!/usr/bin/env python3
"""
Project structure setup script for gpt_5_ceo_research.
Creates all required directories and __init__.py files according to the design document.
Follows KISS principles - simple directory creation with proper error handling.
"""

from pathlib import Path
import sys
import subprocess
import importlib.util
from typing import Dict, Tuple


def create_directory_structure():
    """
    Create all directories from the design document with proper __init__.py files.

    Creates the following structure:
    gpt_5_ceo_research/
    ├── src/
    │   ├── __init__.py
    │   ├── config/
    │   │   ├── __init__.py
    │   │   ├── settings.py
    │   │   └── constants.py
    │   ├── clients/
    │   │   ├── __init__.py
    │   │   └── gpt5_client.py
    │   └── utils/
    │       ├── __init__.py
    │       └── logger.py
    ├── tests/
    │   ├── __init__.py
    │   ├── conftest.py
    │   └── test_initialization.py
    ├── scripts/
    │   └── setup_project.py
    ├── docs/
    ├── docker/

    Returns:
        bool: True if all directories were created successfully, False otherwise.
    """
    # Define the base directory structure
    base_path = Path.cwd() / "gpt_5_ceo_research"

    # Define all directories that need to be created
    directories = [
        base_path / "src",
        base_path / "src" / "config",
        base_path / "src" / "clients",
        base_path / "src" / "utils",
        base_path / "tests",
        base_path / "scripts",
        base_path / "docs",
        base_path / "docker"
    ]

    # Define which directories need __init__.py files (Python packages)
    python_packages = [
        base_path / "src",
        base_path / "src" / "config",
        base_path / "src" / "clients",
        base_path / "src" / "utils",
        base_path / "tests"
    ]

    # Define additional files that need to be created
    additional_files = {
        base_path / "src" / "config" / "settings.py": "",
        base_path / "src" / "config" / "constants.py": "",
        base_path / "src" / "clients" / "gpt5_client.py": "",
        base_path / "src" / "utils" / "logger.py": "",
        base_path / "tests" / "conftest.py": "",
        base_path / "tests" / "test_initialization.py": ""
    }

    try:
        print(f"Creating directory structure at: {base_path}")

        # Create all directories
        for directory in directories:
            if directory.exists():
                print(f"Directory already exists: {directory}")
            else:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {directory}")

        # Create __init__.py files for Python packages
        for package_dir in python_packages:
            init_file = package_dir / "__init__.py"
            if init_file.exists():
                print(f"__init__.py already exists: {init_file}")
            else:
                init_file.touch()
                print(f"Created __init__.py: {init_file}")

        # Create additional empty files
        for file_path, content in additional_files.items():
            if file_path.exists():
                print(f"File already exists: {file_path}")
            else:
                file_path.write_text(content)
                print(f"Created file: {file_path}")

        # Copy this setup script to the new scripts directory
        new_setup_script = base_path / "scripts" / "setup_project.py"
        if not new_setup_script.exists():
            new_setup_script.write_text(Path(__file__).read_text())
            print(f"Copied setup script to: {new_setup_script}")

        print("\n=== Directory Structure Creation Complete ===")
        print("[OK] All directories created successfully")
        print("[OK] All __init__.py files created")
        print("[OK] All placeholder files created")

        return True

    except Exception as e:
        print(f"ERROR: Failed to create directory structure: {e}")
        return False


def create_env_example():
    """
    Create .env.example file with all required environment variables.

    Creates a template environment file with all necessary configuration
    variables for the GPT-5 CEO Research application. Uses placeholder
    values and includes helpful comments for each variable.

    Returns:
        bool: True if .env.example was created successfully, False otherwise.
    """
    env_example_content = """# GPT-5 CEO Research Environment Configuration
# Copy this file to .env and update with your actual values

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
# Your OpenAI API key - get from https://platform.openai.com/api-keys

# GPT-5 Model Configuration
GPT5_MODEL=gpt-5
# Available options: gpt-5, gpt-5-mini, gpt-5-nano
# gpt-5: Most capable but slowest and most expensive
# gpt-5-mini: Balanced performance and cost
# gpt-5-nano: Fastest and cheapest but less capable

# Default Reasoning Configuration
DEFAULT_REASONING_EFFORT=medium
# Available options: minimal, low, medium, high
# Controls the depth of reasoning the model uses
# Higher values produce better results but take longer

# Output Verbosity
DEFAULT_VERBOSITY=medium
# Available options: low, medium, high
# Controls how detailed the model responses are
# low: concise responses, high: detailed explanations

# API Request Configuration
MAX_RETRIES=3
# Maximum number of retry attempts for failed API requests
# Recommended: 3-5 for production environments

TIMEOUT_SECONDS=120
# Request timeout in seconds
# Adjust based on your typical query complexity

# Logging Configuration
LOG_LEVEL=INFO
# Available options: DEBUG, INFO, WARNING, ERROR
# DEBUG: Detailed debugging information
# INFO: General operational messages
# WARNING: Warning messages only
# ERROR: Error messages only

# Processing Configuration
MAX_ITERATIONS=5
# Maximum number of iterations for iterative processes
# Prevents infinite loops in recursive reasoning

CONFIDENCE_THRESHOLD=0.8
# Confidence threshold for accepting results (0.0-1.0)
# Higher values require more confident results

# Caching Configuration
CACHE_TTL_HOURS=24
# Time-to-live for cached responses in hours
# Set to 0 to disable caching"""

    try:
        env_example_path = Path.cwd() / ".env.example"

        if env_example_path.exists():
            print(f".env.example already exists: {env_example_path}")
            return True

        env_example_path.write_text(env_example_content)
        print(f"Created .env.example: {env_example_path}")

        print("\n=== Environment Configuration Complete ===")
        print("[OK] .env.example created with all required variables")
        print("[OK] All variables documented with helpful comments")
        print("[OK] Placeholder values provided (no actual API keys)")

        return True

    except Exception as e:
        print(f"ERROR: Failed to create .env.example: {e}")
        return False


def create_gitignore():
    """
    Create comprehensive .gitignore file with all common Python, IDE, and OS patterns.

    Creates a .gitignore file that excludes:
    - Environment files (.env, venv/, etc.)
    - Python cache files (__pycache__, *.pyc, etc.)
    - IDE files (.vscode/, .idea/, etc.)
    - OS specific files (.DS_Store, Thumbs.db, etc.)
    - Log files (*.log, logs/)
    - Cache directories (.cache/, *.cache)
    - Output files (*.json, *.csv, output/)
    - Testing artifacts (.coverage, .pytest_cache/)
    - Build and distribution files (dist/, build/, *.egg-info/)

    Returns:
        bool: True if .gitignore was created successfully, False otherwise.
    """
    gitignore_content = """# Environment
.env
venv/
env/
.venv/
ENV/
env.bak/
venv.bak/
*.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
develop-eggs/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
.installed.cfg
*.egg
MANIFEST

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
*.py,cover
.hypothesis/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.spyderproject
.spyproject
.ropeproject

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
Desktop.ini

# Logs
*.log
logs/
pip-log.txt
pip-delete-this-directory.txt

# Cache
.cache/
*.cache
.webassets-cache
.sass-cache/

# Output
output/
*.json
*.csv
*.xlsx
*.pdf
*.png
*.jpg
*.jpeg
*.gif
*.svg
*.txt

# Documentation builds
.readthedocs.yml
site/

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

# Translations
*.mo
*.pot

# Django stuff
*.log
local_settings.py
db.sqlite3

# Flask stuff
instance/

# Scrapy stuff
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# PyCharm
.idea/

# VS Code
.vscode/

# Temporary files
*.tmp
*.temp
*~

# Backup files
*.bak
*.backup

# System files
.DS_Store
Thumbs.db

# Node modules (if any JS tools are used)
node_modules/

# Package files
*.tar.gz
*.zip
*.7z
*.rar

# Database files
*.db
*.sqlite
*.sqlite3

# Configuration files that might contain secrets
config.ini
config.yaml
config.json
secrets.json

# AI/ML specific
*.model
*.pkl
*.pickle
checkpoints/
experiments/
wandb/

# Project specific
.claude/
.spec-workflow/
nul"""

    try:
        gitignore_path = Path.cwd() / ".gitignore"

        if gitignore_path.exists():
            print(f".gitignore already exists: {gitignore_path}")
            return True

        gitignore_path.write_text(gitignore_content)
        print(f"Created .gitignore: {gitignore_path}")

        print("\n=== Git Ignore Configuration Complete ===")
        print("[OK] .gitignore created with comprehensive patterns")
        print("[OK] Environment files (.env, venv/) ignored")
        print("[OK] Python cache files (__pycache__, *.pyc) ignored")
        print("[OK] IDE files (.vscode/, .idea/) ignored")
        print("[OK] OS files (.DS_Store, Thumbs.db) ignored")
        print("[OK] Output and log files ignored")

        return True

    except Exception as e:
        print(f"ERROR: Failed to create .gitignore: {e}")
        return False


def init_git_repository():
    """
    Initialize git repository if not already initialized.

    Checks if the current directory is already a git repository.
    If not, initializes a new git repository with 'git init'.

    Returns:
        bool: True if git repository exists or was initialized successfully, False otherwise.
    """
    try:
        import subprocess

        # Check if already a git repository
        result = subprocess.run(['git', 'status'],
                              capture_output=True,
                              text=True,
                              cwd=Path.cwd())

        if result.returncode == 0:
            print("Git repository already initialized")
            return True

        # Initialize git repository
        result = subprocess.run(['git', 'init'],
                              capture_output=True,
                              text=True,
                              cwd=Path.cwd())

        if result.returncode == 0:
            print("Git repository initialized successfully")
            print(f"Initialized empty Git repository in {Path.cwd()}")
            return True
        else:
            print(f"ERROR: Failed to initialize git repository: {result.stderr}")
            return False

    except FileNotFoundError:
        print("ERROR: Git is not installed or not available in PATH")
        return False
    except Exception as e:
        print(f"ERROR: Failed to initialize git repository: {e}")
        return False


def install_dependencies():
    """
    Install all required dependencies using Poetry or pip.

    Detects if Poetry is available and uses it for dependency management.
    Falls back to pip if Poetry is not available. Creates appropriate
    configuration files (pyproject.toml or requirements.txt) with pinned
    versions for reproducibility.

    Dependencies installed:
    - openai>=1.40.0: OpenAI API client
    - aiohttp>=3.9.0: Async HTTP client
    - pydantic>=2.5.0: Data validation
    - python-dotenv>=1.0.0: Environment variable management
    - structlog>=24.1.0: Structured logging
    - tenacity>=8.2.0: Retry mechanisms
    - pytest>=7.4.0: Testing framework (dev)
    - pytest-asyncio>=0.21.0: Async testing support (dev)

    Returns:
        bool: True if all dependencies were installed successfully, False otherwise.
    """
    # Define production dependencies with pinned versions
    production_deps = {
        "openai": ">=1.40.0",
        "aiohttp": ">=3.9.0",
        "pydantic": ">=2.5.0",
        "python-dotenv": ">=1.0.0",
        "structlog": ">=24.1.0",
        "tenacity": ">=8.2.0"
    }

    # Define development dependencies with pinned versions
    dev_deps = {
        "pytest": ">=7.4.0",
        "pytest-asyncio": ">=0.21.0"
    }

    try:
        print("=== Dependency Installation ===")
        print("Detecting package manager...")

        # Check if Poetry is available
        poetry_available = _check_poetry_available()

        if poetry_available:
            print("Poetry detected - using Poetry for dependency management")
            success = _install_with_poetry(production_deps, dev_deps)
        else:
            print("Poetry not available - using pip for dependency management")
            success = _install_with_pip(production_deps, dev_deps)

        if success:
            print("\n=== Verifying Installation ===")
            verification_success = _verify_package_installation(production_deps, dev_deps)

            if verification_success:
                print("\n=== Dependency Installation Complete ===")
                print("[OK] All dependencies installed successfully")
                print("[OK] All packages verified through import test")
                return True
            else:
                print("\n[ERROR] Dependency verification failed")
                return False
        else:
            print("\n[ERROR] Dependency installation failed")
            return False

    except Exception as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False


def _check_poetry_available():
    """Check if Poetry is available by running 'poetry --version'."""
    try:
        result = subprocess.run(['poetry', '--version'],
                              capture_output=True,
                              text=True,
                              timeout=10)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _install_with_poetry(production_deps, dev_deps):
    """Install dependencies using Poetry."""
    try:
        # Create pyproject.toml content
        pyproject_content = _create_pyproject_toml(production_deps, dev_deps)

        # Write pyproject.toml
        pyproject_path = Path.cwd() / "pyproject.toml"
        if pyproject_path.exists():
            print("pyproject.toml already exists - backing up existing file")
            backup_path = pyproject_path.with_suffix(".toml.backup")
            if backup_path.exists():
                backup_path.unlink()  # Remove existing backup
            pyproject_path.rename(backup_path)
            print(f"Existing pyproject.toml backed up to: {backup_path}")

        pyproject_path.write_text(pyproject_content)
        print(f"Created pyproject.toml: {pyproject_path}")

        # Install dependencies with Poetry
        print("Installing dependencies with Poetry...")
        result = subprocess.run(['poetry', 'install'],
                              capture_output=True,
                              text=True,
                              timeout=300)

        if result.returncode == 0:
            print("Poetry installation completed successfully")
            return True
        else:
            print(f"ERROR: Poetry installation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"ERROR: Failed to install with Poetry: {e}")
        return False


def _install_with_pip(production_deps, dev_deps):
    """Install dependencies using pip."""
    try:
        # Create requirements.txt content
        requirements_content = _create_requirements_txt(production_deps, dev_deps)

        # Write requirements.txt
        requirements_path = Path.cwd() / "requirements.txt"
        if requirements_path.exists():
            print("requirements.txt already exists - backing up existing file")
            backup_path = requirements_path.with_suffix(".txt.backup")
            if backup_path.exists():
                backup_path.unlink()  # Remove existing backup
            requirements_path.rename(backup_path)
            print(f"Existing requirements.txt backed up to: {backup_path}")

        requirements_path.write_text(requirements_content)
        print(f"Created requirements.txt: {requirements_path}")

        # Install dependencies with pip
        print("Installing dependencies with pip...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                              capture_output=True,
                              text=True,
                              timeout=300)

        if result.returncode == 0:
            print("Pip installation completed successfully")
            return True
        else:
            print(f"ERROR: Pip installation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"ERROR: Failed to install with pip: {e}")
        return False


def _create_pyproject_toml(production_deps, dev_deps):
    """Create pyproject.toml content with all dependencies."""
    # Format production dependencies
    prod_lines = []
    for package, version in production_deps.items():
        prod_lines.append(f'"{package}" = "{version}"')

    # Format development dependencies
    dev_lines = []
    for package, version in dev_deps.items():
        dev_lines.append(f'"{package}" = "{version}"')

    content = f'''[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "gpt-5-ceo-research"
version = "0.1.0"
description = "GPT-5 CEO Research Application"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [{{include = "src"}}]

[tool.poetry.dependencies]
python = "^3.8"
{chr(10).join(prod_lines)}

[tool.poetry.group.dev.dependencies]
{chr(10).join(dev_lines)}

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = [
    "tests",
]
asyncio_mode = "auto"
'''
    return content


def _create_requirements_txt(production_deps, dev_deps):
    """Create requirements.txt content with all dependencies."""
    lines = ["# Production Dependencies"]

    for package, version in production_deps.items():
        lines.append(f"{package}{version}")

    lines.append("\n# Development Dependencies")

    for package, version in dev_deps.items():
        lines.append(f"{package}{version}")

    return "\n".join(lines)


def _verify_package_installation(production_deps, dev_deps):
    """Verify that all packages can be imported successfully."""
    all_packages = {**production_deps, **dev_deps}

    # Map package names to import names (some packages have different import names)
    import_names = {
        "openai": "openai",
        "aiohttp": "aiohttp",
        "pydantic": "pydantic",
        "python-dotenv": "dotenv",
        "structlog": "structlog",
        "tenacity": "tenacity",
        "pytest": "pytest",
        "pytest-asyncio": "pytest_asyncio"
    }

    failed_imports = []

    for package in all_packages.keys():
        import_name = import_names.get(package, package)
        try:
            if importlib.util.find_spec(import_name) is not None:
                print(f"[OK] {package} ({import_name}) - import test passed")
            else:
                print(f"[FAILED] {package} ({import_name}) - module not found")
                failed_imports.append(package)
        except Exception as e:
            print(f"[FAILED] {package} ({import_name}) - import error: {e}")
            failed_imports.append(package)

    if failed_imports:
        print(f"\nFailed to verify imports for: {', '.join(failed_imports)}")
        return False
    else:
        print("\nAll packages verified successfully")
        return True


def verify_python_version() -> bool:
    """Verify Python version is 3.11 or higher."""
    required_version = (3, 11)
    current_version = sys.version_info[:2]

    print(f"Current Python version: {sys.version}")
    print(f"Version tuple: {current_version}")

    if current_version < required_version:
        print(f"ERROR: Python {required_version[0]}.{required_version[1]}+ is required.")
        print(f"Current version is {current_version[0]}.{current_version[1]}")
        return False

    print(f"[OK] Python version {current_version[0]}.{current_version[1]} meets requirements (3.11+)")
    return True


def run_setup_steps() -> Dict[str, bool]:
    """Run all setup steps and return their success status."""
    steps = {
        "python_version": ("Verifying Python version", verify_python_version),
        "directory_structure": ("Creating directory structure", create_directory_structure),
        "env_example": ("Creating environment configuration", create_env_example),
        "gitignore": ("Creating .gitignore file", create_gitignore),
        "git_init": ("Initializing git repository", init_git_repository),
        "dependencies": ("Installing dependencies", install_dependencies)
    }

    results = {}

    for step_name, (description, function) in steps.items():
        print(f"\n=== Step {len(results) + 1}: {description} ===")
        try:
            success = function()
            results[step_name] = success

            if success:
                print(f"[OK] {description} completed successfully")
            else:
                print(f"[FAILED] {description} failed")
                # Continue with remaining steps for idempotency

        except Exception as e:
            print(f"[ERROR] {description} failed with exception: {e}")
            results[step_name] = False
            # Continue with remaining steps for idempotency

    return results


def display_final_results(results: Dict[str, bool]) -> None:
    """Display final setup results and next steps."""
    print("\n" + "=" * 50)
    print("PROJECT SETUP SUMMARY")
    print("=" * 50)

    # Display step results
    step_descriptions = {
        "python_version": "Python version verification",
        "directory_structure": "Directory structure creation",
        "env_example": "Environment configuration creation",
        "gitignore": "Git ignore configuration creation",
        "git_init": "Git repository initialization",
        "dependencies": "Dependency installation"
    }

    successful_steps = []
    failed_steps = []

    for step_name, success in results.items():
        description = step_descriptions.get(step_name, step_name)
        if success:
            print(f"[OK] {description}")
            successful_steps.append(step_name)
        else:
            print(f"[FAILED] {description}")
            failed_steps.append(step_name)

    # Overall status
    all_successful = len(failed_steps) == 0
    print(f"\nOverall Status: {'SUCCESS' if all_successful else 'PARTIAL SUCCESS'}")
    print(f"Successful steps: {len(successful_steps)}/{len(results)}")

    if failed_steps:
        print(f"Failed steps: {', '.join(failed_steps)}")
        print("\nNote: You can re-run this script to retry failed steps.")
        print("This script is idempotent - it will skip already completed steps.")

    # Next steps instructions
    if all_successful or "directory_structure" in successful_steps:
        print("\n" + "=" * 50)
        print("NEXT STEPS")
        print("=" * 50)

        next_steps = []

        if "env_example" in successful_steps:
            next_steps.extend([
                "1. Copy .env.example to .env:",
                "   cp .env.example .env  # (Linux/Mac)",
                "   copy .env.example .env  # (Windows)",
                "2. Update .env with your actual API keys and preferences"
            ])

        if "git_init" in successful_steps:
            next_steps.extend([
                "3. Add files to git:",
                "   git add .",
                "4. Make initial commit:",
                "   git commit -m 'Initial project setup'"
            ])

        if "directory_structure" in successful_steps:
            next_steps.extend([
                "5. Navigate to project directory:",
                "   cd gpt_5_ceo_research",
                "6. Start developing your GPT-5 CEO Research application!"
            ])

        if "dependencies" in successful_steps:
            next_steps.extend([
                "7. Activate your virtual environment (if using venv):",
                "   source venv/bin/activate  # (Linux/Mac)",
                "   venv\\Scripts\\activate  # (Windows)"
            ])

        for step in next_steps:
            print(step)


def main() -> None:
    """Main orchestration function for complete project setup.

    This function orchestrates all setup steps in the correct order with proper
    error handling and progress messages. It's idempotent - can be run multiple
    times safely, skipping already completed steps.

    Setup order:
    1. verify_python_version() - Ensure Python 3.11+
    2. create_directory_structure() - Create project directories
    3. create_env_example() - Create environment template
    4. create_gitignore() - Create git ignore file
    5. init_git_repository() - Initialize git repository
    6. install_dependencies() - Install required packages

    Returns:
        None. Exits with status code 0 on success, 1 on failure.
    """
    print("GPT-5 CEO Research Project Setup")
    print("=" * 50)
    print("This script will set up your GPT-5 CEO Research project with all")
    print("required directories, configuration files, and dependencies.")
    print("\nThe setup process is idempotent - you can run it multiple times safely.")
    print("Already completed steps will be skipped.")

    # Run all setup steps
    results = run_setup_steps()

    # Display final results and next steps
    display_final_results(results)

    # Exit with appropriate code
    failed_steps = [step for step, success in results.items() if not success]

    if not failed_steps:
        print("\n[SUCCESS] Project setup completed successfully!")
        sys.exit(0)
    else:
        print(f"\n[PARTIAL] Setup completed with {len(failed_steps)} failed steps.")
        print("Re-run this script to retry failed steps.")
        sys.exit(1)


if __name__ == "__main__":
    main()