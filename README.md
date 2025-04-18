# DICOM Sender

A Python-based GUI application for sending DICOM files to PACS servers with DICOM echo functionality. Uses the dcm4che Java library for DICOM network operations.

## Features

- Send DICOM files to PACS servers via dcm4che's storescu
- DICOM Echo functionality to test server connectivity via dcm4che's echoscu
- Support for all DICOM transfer syntaxes supported by dcm4che
- Configurable server settings (IP, Port, AE Title)
- Save default settings
- Detailed logging
- Modern UI using CustomTkinter

## Quick Start - Standalone Executable

For Windows users who don't want to install Python, a standalone executable is available:

1. Download the `DICOM_Sender_v1.1.0.zip` file from this repository
2. Extract the ZIP file to any location on your computer
3. Run `DICOM_Sender.exe` directly - no installation needed!

The ZIP package contains everything needed to run the application, including all dependencies and libraries. The only prerequisite is having Java Runtime Environment (JRE) 8 or higher installed on your system.

## Requirements (for source code users)

- Python 3.7 or higher
- Java Runtime Environment (JRE) 8 or higher
- Required Python packages are listed in `requirements.txt`
  - CustomTkinter - Modern UI library based on Tkinter
  - pydicom - For DICOM file handling (metadata only)
- dcm4che Java library (see installation instructions)

## Installation (from source)

1. Clone the repository:
   ```bash
   git clone https://github.com/johnAlexamon/dicom_sender.git
   cd dicom_sender
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install dcm4che library:
   - Download from https://sourceforge.net/projects/dcm4che/files/dcm4che3/
   - Place required JAR files in the `lib/dcm4che/lib` directory
   - See `lib/dcm4che/README.md` for detailed instructions

## Usage

1. Run the application:
   - If using the standalone executable: double-click `DICOM_Sender.exe`
   - If using source code: `python dicom_sender.py`

2. Configure the PACS server settings:
   - Server IP
   - Port
   - AE Title

3. Use "DICOM Echo" to test the connection

4. Select a DICOM file and click "Send DICOM" to transmit

## Logging

The application creates detailed logs in the application directory with timestamps. Log files follow the naming pattern: `dicom_sender_YYYYMMDD_HHMMSS.log`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The dcm4che libraries used in this project are licensed under the Mozilla Public License Version 1.1.
See [dcm4che's license](https://github.com/dcm4che/dcm4che/blob/master/LICENSE.txt) for details. 