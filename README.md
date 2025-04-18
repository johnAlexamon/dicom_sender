# DICOM Sender

A Python-based GUI application for sending DICOM files to PACS servers with DICOM echo functionality.

## Features

- Send DICOM files to PACS servers
- DICOM Echo functionality to test server connectivity
- Support for JPEG 2000 compressed DICOM files
- Configurable server settings (IP, Port, AE Title)
- Save default settings
- Detailed logging

## Requirements

- Python 3.7 or higher
- Required Python packages are listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/johnAlexamon/dicom_sender.git
   cd dicom_sender
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python dicom_sender.py
   ```

2. Configure the PACS server settings:
   - Server IP
   - Port
   - AE Title

3. Use "DICOM Echo" to test the connection

4. Select a DICOM file and click "Send DICOM" to transmit

## Logging

The application creates detailed logs in the application directory with timestamps. Log files follow the naming pattern: `dicom_sender_YYYYMMDD_HHMMSS.log` 