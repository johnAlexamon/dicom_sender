# Project Structure

## Overview

The Alexamon DICOM Sender project follows a standardized directory structure:

```
alexamon-dicom-sender/
├── src/                # All source code must be here
│   ├── __init__.py     # Package initialization with version
│   ├── dicom_sender.py # Main application code
│   └── utils/          # Utility modules
│       ├── __init__.py
│       ├── download_dcm4che.py  # Script to download dcm4che library
│       └── move_active_logs.py  # Script to manage log files
├── logs/               # Log files only
├── releases/           # Release ZIP files only 
├── lib/                # External libraries
│   └── dcm4che/        # dcm4che Java library
├── resources/          # Application resources (icons, etc.)
├── docs/               # Documentation files
│   ├── structure.md    # This file
│   └── project_rules.md # Project rules and standards
├── tests/              # Test files
├── main.py             # Entry point (ONLY Python file in root)
├── README.md           # Project overview
├── LICENSE             # MIT License
└── requirements.txt    # Python dependencies
```

## Key Components

- **main.py**: The entry point for running the application (imports from src)
- **src/dicom_sender.py**: The main application code with GUI and DICOM sending functionality
- **src/utils/**: Utility modules for the application
- **lib/dcm4che/**: Directory containing the dcm4che Java library and dependencies
- **logs/**: Directory where log files are stored (excluded from git)
- **releases/**: Directory where release ZIP files are stored (excluded from git)

## Documentation

Please refer to `docs/project_rules.md` for detailed information on project structure standards and rules for maintaining consistency in the codebase. 