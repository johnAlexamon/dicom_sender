# DICOM Sender

A simple GUI application for sending DICOM files to a DICOM server using C-STORE.

## Features

- Modern, user-friendly interface
- Select DICOM files from your local system
- Configure server IP, port, and AE Title
- Send DICOM files using C-STORE
- Real-time status updates

## Setup

1. Install Python 3.8 or higher if you haven't already
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

Simply run:
```
python dicom_sender.py
```

## Usage

1. Enter the DICOM server details:
   - Server IP address
   - Port number
   - AE Title (Application Entity Title)
2. Click "Select DICOM File" to choose a DICOM file from your system
3. Click "Send DICOM" to transmit the file to the server
4. The status label will show the result of the operation

## Creating a Standalone Executable

To create a standalone executable that doesn't require Python installation:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create the executable:
   ```
   pyinstaller --onefile --windowed dicom_sender.py
   ```

The executable will be created in the `dist` directory. 