#!/usr/bin/env python3
"""
Alexamon DICOM Sender - Main Entry Point

This file serves as the entry point for running the Alexamon DICOM Sender application.
It imports the application from the src package and runs it.
"""

import sys
import os
import logging

# Add the project root to the Python path if not already there
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        # Import and run the application
        from src.dicom_sender import DicomSenderApp
        app = DicomSenderApp()
        app.mainloop()
    except Exception as e:
        logging.exception("Error running application")
        print(f"Error: {str(e)}")
        sys.exit(1) 