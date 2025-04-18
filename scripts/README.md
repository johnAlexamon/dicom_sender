# DICOM Modification and Sending Test Scripts

This directory contains test scripts for working with DICOM files using dcm4che.

## Prerequisites

- Python 3.8 or higher
- Java 11 or higher
- dcm4che library (installed in the lib/dcm4che directory)
- pydicom package (for Python DICOM file handling)

## Available Scripts

### 1. Test DICOM Tag Modification (`test_dicom_tag_modification.py`)

Tests the modification of DICOM tags in a file.

```
python scripts/test_dicom_tag_modification.py --file <path_to_dicom_file> --tag "<tag>=<value>" [--tag "<tag>=<value>" ...]
```

Example:
```
python scripts/test_dicom_tag_modification.py --file "temp_dcm4che/dcm4che-5.33.1/etc/testdata/dicom/MR01.dcm" --tag "00100020=TEST_ID" --tag "00100010=TEST^PATIENT"
```

### 2. Test Modify and Send (`test_modify_and_send.py`)

Tests both modification of DICOM tags and sending to a DICOM server.

```
python scripts/test_modify_and_send.py --file <path_to_dicom_file> --ip <server_ip> --port <server_port> --ae-title <ae_title> --tag "<tag>=<value>" [--tag "<tag>=<value>" ...]
```

Example:
```
python scripts/test_modify_and_send.py --file "temp_dcm4che/dcm4che-5.33.1/etc/testdata/dicom/MR01.dcm" --ip 127.0.0.1 --port 11112 --ae-title ORTHANC --tag "00100020=MODIFIED_ID" --tag "00100010=MODIFIED^PATIENT"
```

### 3. Anonymize DICOM Files (`anonymize_dicom.py`)

Creates anonymized versions of DICOM files for testing purposes by modifying patient-identifying information.

```
python scripts/anonymize_dicom.py --file <path_to_dicom_file> [--output <output_path>] [--randomize]
```

To anonymize an entire folder of DICOM files:

```
python scripts/anonymize_dicom.py --folder <path_to_dicom_folder> [--output <output_folder>] [--randomize]
```

Options:
- `--randomize`: Use random values for patient information instead of the default "ANONYMOUS" values
- `--output`: Specify custom output file/folder (optional)

Example:
```
python scripts/anonymize_dicom.py --file "temp_dcm4che/dcm4che-5.33.1/etc/testdata/dicom/MR01.dcm" --randomize
```

### 4. Batch Process DICOM Files (`batch_processor.py`)

A multithreaded utility for batch processing DICOM files, supporting anonymization, sending, and tag modification operations.

```
python scripts/batch_processor.py --folder <folder_path> --anonymize [--output-dir <output_dir>] [--randomize] [--workers 8]
```

```
python scripts/batch_processor.py --folder <folder_path> --send --ip <server_ip> --port <port> --ae-title <ae_title> [--workers 8]
```

```
python scripts/batch_processor.py --folder <folder_path> --modify-and-send --ip <server_ip> --port <port> --ae-title <ae_title> --tag "<tag>=<value>" [--tag "<tag>=<value>" ...] [--workers 8]
```

Key features:
- Multithreaded processing with configurable number of worker threads
- Progress reporting
- Detailed success/error statistics
- Support for processing a single file or an entire folder of DICOM files

Examples:

1. Anonymize all DICOM files in a folder with random values:
```
python scripts/batch_processor.py --folder "patient_data" --anonymize --output-dir "anonymized_data" --randomize --workers 8
```

2. Send all DICOM files in a folder to a PACS server:
```
python scripts/batch_processor.py --folder "dicom_files" --send --ip 192.168.1.100 --port 11112 --ae-title ORTHANC
```

3. Modify patient ID and name, then send to a PACS server:
```
python scripts/batch_processor.py --folder "dicom_files" --modify-and-send --ip 192.168.1.100 --port 11112 --ae-title ORTHANC --tag "00100020=TESTID" --tag "00100010=TEST^PATIENT"
```

## DICOM Tag Reference

Common DICOM tags that you might want to modify:

| Tag       | Name                | Description            |
|-----------|---------------------|------------------------|
| 00100010  | PatientName         | Patient's full name    |
| 00100020  | PatientID           | Patient identifier     |
| 00100030  | PatientBirthDate    | Birth date             |
| 00100040  | PatientSex          | Patient's sex          |
| 00080020  | StudyDate           | Date of study          |
| 00080030  | StudyTime           | Time of study          |
| 00080090  | ReferringPhysician  | Referring doctor       |
| 00081030  | StudyDescription    | Study description      |

## Summary of Tool Capabilities

This toolkit provides comprehensive DICOM workflow capabilities:

1. **DICOM File Operations**
   - Send DICOM files to PACS servers (single file or batch)
   - Verify PACS connectivity with DICOM Echo
   - Find DICOM files in folders (with or without .dcm extension)
   
2. **Tag Modification**
   - Change patient identifiers and metadata
   - Directly edit any DICOM tag with proper VR handling
   - Uses dcm4che3's Java libraries for robust modification
   
3. **Anonymization**
   - Remove or anonymize patient-identifying information
   - Generate random but valid patient data
   - Process individual files or entire directories
   
4. **Batch Processing**
   - Multithreaded processing for large datasets
   - Combine operations (modify + send, anonymize + save)
   - Detailed progress reporting and statistics

All tools are built on the dcm4che Java library, ensuring full DICOM standard compliance. The Python interface makes these powerful tools accessible and easy to integrate into your workflow.

## Notes

1. If the DICOM server is not available or doesn't respond to the echo request, the script will still attempt to modify the tags and send the file.
2. Modified files are stored in a temporary directory.
3. Tag values can contain spaces, but make sure to enclose the entire tag-value pair in quotes. 