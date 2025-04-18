# Release Process

This document outlines the process for creating new releases of the Alexamon DICOM Sender application.

## Prerequisites

- Python 3.8+ with pip
- PyInstaller package (`pip install pyinstaller`)
- Git command line tools

## Version Update Steps

1. Update the version number in `src/__init__.py`:
   ```python
   __version__ = "x.y.z"  # Replace with new version
   ```

2. Update the `CHANGELOG.md` with details of changes in the new version.

3. Commit these changes:
   ```bash
   git add src/__init__.py CHANGELOG.md
   git commit -m "Bump version to x.y.z"
   ```

4. Create a git tag for the new version:
   ```bash
   git tag vx.y.z
   ```

5. Push the changes and tag to GitHub:
   ```bash
   git push origin master
   git push origin vx.y.z
   ```

## Building with PyInstaller

To build the application package:

1. Run PyInstaller with the following command from the root directory:

   ```bash
   # Windows (PowerShell)
   python -m PyInstaller --noconfirm --onedir --windowed --add-data "lib;lib" --name "Alexamon_DICOM_Sender" main.py

   # macOS/Linux
   python -m PyInstaller --noconfirm --onedir --windowed --add-data "lib:lib" --name "Alexamon_DICOM_Sender" main.py
   ```

   This command:
   - Creates a directory-based distribution (`--onedir`)
   - Builds a windowed application without console (`--windowed`)
   - Includes the `lib` directory with dcm4che and other dependencies
   - Names the output "Alexamon_DICOM_Sender"

2. The built application will be in the `dist/Alexamon_DICOM_Sender` directory.

## Creating the Release ZIP

After building with PyInstaller:

1. Create a ZIP file of the application with the correct version number:

   ```bash
   # Windows (PowerShell)
   cd dist
   Compress-Archive -Path "Alexamon_DICOM_Sender" -DestinationPath "../releases/Alexamon_DICOM_Sender_vx.y.z.zip" -Force
   cd ..

   # macOS/Linux
   cd dist
   zip -r "../releases/Alexamon_DICOM_Sender_vx.y.z.zip" "Alexamon_DICOM_Sender"
   cd ..
   ```

2. Verify the ZIP file was created correctly:
   ```bash
   # Check the file exists and size is reasonable
   dir releases/Alexamon_DICOM_Sender_vx.y.z.zip
   ```

## Publishing the Release

1. The ZIP file is now ready in the `releases` directory.
2. This file can be uploaded to GitHub as an official release.
3. Update the documentation as needed to reference the new version.

## Troubleshooting

- If PyInstaller fails, check the warnings file at `build/Alexamon_DICOM_Sender/warn-Alexamon_DICOM_Sender.txt`
- Ensure all dependencies are installed in your environment
- For more detailed logs, add the `--log-level DEBUG` option to PyInstaller

## Requirements for a Valid Release

Every release must include:
1. Updated version in source code
2. Git tag matching the version
3. Updated changelog
4. Properly built ZIP package in the releases directory 