# Project Structure

## Overview

The Alexamon DICOM Sender project is organized as follows:

```
alexamon-dicom-sender/
├── src/                # Source code directory
│   ├── __init__.py     # Package initialization
│   ├── dicom_sender.py # Main application code
│   ├── utils/          # Utility modules
│   │   ├── __init__.py
│   │   ├── download_dcm4che.py  # Script to download dcm4che library
│   │   └── move_active_logs.py  # Script to manage log files
├── logs/               # Log files
├── releases/           # Release files (ZIP packages)
├── lib/                # External libraries
│   └── dcm4che/        # dcm4che Java library
├── resources/          # Resources (icons, etc.)
├── docs/               # Documentation
├── tests/              # Tests for the code
├── main.py             # Entry point for the application
├── README.md           # Project overview
├── LICENSE             # MIT License
└── requirements.txt    # Python dependencies
```

## Key Components

- **src/dicom_sender.py**: The main application code containing the GUI and DICOM sending functionality
- **src/utils/download_dcm4che.py**: Utility script to download and set up the dcm4che library
- **lib/dcm4che/**: Directory containing the dcm4che Java library and dependencies
- **main.py**: The entry point for running the application
- **logs/**: Directory where log files are stored
- **releases/**: Directory where release ZIP files are stored locally (not in git) 