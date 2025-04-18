# Alexamon DICOM Sender - Project Rules

This document outlines the standards and rules for maintaining the Alexamon DICOM Sender project structure.

## Directory Structure

```
alexamon-dicom-sender/
├── src/                # All source code must be here
│   ├── __init__.py     # Package initialization with version
│   ├── dicom_sender.py # Main application code
│   └── utils/          # Utility modules
│       ├── __init__.py
│       └── [utility].py
├── logs/               # Log files only
├── releases/           # Release ZIP files only
├── lib/                # External libraries
├── resources/          # Application resources (icons, etc.)
├── docs/               # Documentation files
├── tests/              # Test files
├── main.py             # Entry point
├── README.md           # Project overview
├── LICENSE             # MIT License
└── requirements.txt    # Python dependencies
```

## Rules for Key Directories

### Source Code (`src/`)
- **All Python code** must be placed in the `src` directory or its subdirectories
- Organize utility functions in `src/utils/`
- Use proper Python package structure with `__init__.py` files
- Maximum file size: 300 lines of code per file

### Entry Point (`main.py`)
- The only Python file allowed in the root directory is `main.py`
- `main.py` should only import from the `src` package and launch the application

### Release Files (`releases/`)
- All release ZIP files must be stored in the `releases/` directory
- Naming convention: `Alexamon_DICOM_Sender_v{version}.zip`
- Release files should never be committed to git
- When creating a new release:
  1. Increment version number in `src/__init__.py`
  2. Create a git tag with that version number
  3. Build the ZIP package and place it in `releases/`

### Log Files (`logs/`)
- All log files must be stored in the `logs/` directory
- Log files should never be committed to git
- Naming convention: `dicom_sender_YYYYMMDD_HHMMSS.log`

### External Libraries (`lib/`)
- Third-party libraries that aren't installed via pip
- Java libraries and dependencies for dcm4che
- Keep organized in subdirectories by library name

### Configuration
- Configuration files should be stored in the root directory
- `config.json` for application settings

### Documentation (`docs/`)
- All documentation files should be in Markdown format
- Update documentation when making significant changes
- Required docs:
  - `structure.md` - Project structure overview
  - `project_rules.md` - This file
  - Any additional feature-specific documentation

## Git Guidelines

- Never commit:
  - Log files
  - Release ZIP files
  - Build artifacts
  - Cached files (`__pycache__/`, `.pyc`)
  - Configuration files with sensitive information
  
- Always commit:
  - Source code changes
  - Documentation updates
  - Test files
  - CI/CD configuration
  
## Version Control

- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Create a git tag for each release version
- Update version in `src/__init__.py` when making a release

## Building and Packaging

- Use PyInstaller for creating executable packages
- Store build configuration in `file_version_info.txt`
- Place final ZIP files in the `releases/` directory
- Update README with release notes for each version 