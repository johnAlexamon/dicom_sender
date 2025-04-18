# DICOM Sender

A Python-based GUI application for sending DICOM files to PACS servers with DICOM echo functionality. Uses the dcm4che Java library for DICOM network operations.

## Features

- Send DICOM files to PACS servers via dcm4che's storescu
- DICOM Echo functionality to test server connectivity via dcm4che's echoscu
- Support for all DICOM transfer syntaxes supported by dcm4che
- **DICOM tag modification** - Edit DICOM tags before sending (Patient ID, Patient Name, etc.)
- Configurable server settings (IP, Port, AE Title)
- Save default settings
- Detailed logging
- Modern UI using CustomTkinter

## Quick Start - Standalone Executable

For Windows users who don't want to install Python, a standalone executable is available:

1. Download the latest release ZIP file (like `Alexamon_DICOM_Sender_v1.2.0.zip`) from the [GitHub Releases tab](https://github.com/johnAlexamon/dicom_sender/releases)
2. Extract the ZIP file to any location on your computer
3. Run `Alexamon_DICOM_Sender.exe` directly - no installation needed!

The ZIP package contains everything needed to run the application, including all dependencies and libraries. The only prerequisite is having Java Runtime Environment (JRE) 8 or higher installed on your system.

> **Note**: All official releases are published under the GitHub Releases tab. Always download the latest version for the best features and bug fixes.

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

4. Set up the DICOM tag modification utility:
   ```bash
   scripts/setup_dcm4che_modifier.bat
   ```
   This will validate your dcm4che setup and compile the Java utility needed for tag modification.

## Usage

1. Run the application:
   - If using the standalone executable: double-click `Alexamon_DICOM_Sender.exe`
   - If using source code: `python main.py`

2. Configure the PACS server settings:
   - Server IP
   - Port
   - AE Title

3. Use "DICOM Echo" to test the connection

4. Select a DICOM file or folder 

5. (Optional) Modify DICOM tags:
   - Check the tags you want to modify in the DICOM Tag Modification section
   - Enter new values for each tag
   - The modifications will be applied to all selected files during sending

6. Click "Send DICOM" to transmit

## DICOM Tag Modification

The application supports modifying DICOM tags directly using the dcm4che3 Java library. This is a more robust approach than command-line tag modification:

- Uses dcm4che's native Attributes API for proper tag handling
- Preserves file meta information
- Respects correct Value Representation (VR) for each tag

To test tag modification from the command line:

```bash
python scripts/test_dicom_tag_modification.py --file path/to/dicom.dcm --tag "0010,0020=ANONYMOUS" --tag "0010,0010=ANONYMOUS^PATIENT"
```

To test both tag modification and sending in one operation:

```bash
python scripts/test_modify_and_send.py --file path/to/dicom.dcm --ip 127.0.0.1 --port 11112 --ae-title ORTHANC --tag "0010,0020=ANONYMOUS" --tag "0010,0010=ANONYMOUS^PATIENT"
```

See the [Scripts Documentation](scripts/README.md) for more details about available test scripts.

The tag modification feature creates a temporary modified copy of the DICOM file before sending, leaving your original files untouched.

## Project Structure

The project follows a standardized structure:

- `src/` - Contains all source code
- `logs/` - Contains log files
- `releases/` - Contains release ZIP packages
- `lib/` - Contains external libraries like dcm4che
- `docs/` - Contains documentation

For more information about the project structure and development guidelines, see:
- [Project Structure Documentation](docs/structure.md)
- [Project Rules](docs/project_rules.md)
- [Release Process](docs/release_process.md)

## Logging

The application creates detailed logs in the `logs` directory with timestamps. Log files follow the naming pattern: `dicom_sender_YYYYMMDD_HHMMSS.log`. These logs are useful for troubleshooting and tracking activity.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The dcm4che libraries used in this project are licensed under the Mozilla Public License Version 1.1.
See [dcm4che's license](https://github.com/dcm4che/dcm4che/blob/master/LICENSE.txt) for details.

## Testing and Utility Scripts

The project includes several utility scripts for testing and working with DICOM files:

### Included Scripts

1. **Tag Modification Testing**
   ```bash
   python scripts/test_dicom_tag_modification.py --file path/to/dicom.dcm --tag "00100020=TEST_ID" --tag "00100010=TEST^PATIENT"
   ```

2. **Modify and Send Testing**
   ```bash
   python scripts/test_modify_and_send.py --file path/to/dicom.dcm --ip 127.0.0.1 --port 11112 --ae-title ORTHANC --tag "00100020=TEST_ID"
   ```

3. **DICOM Anonymization**
   ```bash
   python scripts/anonymize_dicom.py --folder path/to/dicom_folder --output-dir anonymized_data --randomize
   ```

4. **Batch Processing**
   ```bash
   python scripts/batch_processor.py --folder dicom_files --modify-and-send --ip 127.0.0.1 --port 11112 --ae-title ORTHANC --tag "00100020=TEST_ID"
   ```

These scripts are useful for:
- Testing PACS connectivity
- Preparing anonymized datasets
- Processing large volumes of DICOM files
- Testing tag modification features
- Validating dcm4che integration

See the [Scripts Documentation](scripts/README.md) for detailed information on using these utilities. 