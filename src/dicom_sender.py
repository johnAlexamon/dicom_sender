"""
Alexamon DICOM Sender
Copyright © 2025 Alexamon. All rights reserved.

A DICOM file transfer application using dcm4che Java libraries for PACS connectivity.
"""

import logging
from src.utils.file_helpers import get_log_filename

# Configure logging
log_filename = get_log_filename()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

# Import the UI after logging is configured
from src.ui.main_window import DicomSenderApp

if __name__ == "__main__":
    app = DicomSenderApp()
    app.mainloop() 