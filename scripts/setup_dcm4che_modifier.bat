@echo off
setlocal

echo ======================================
echo DICOM Sender - dcm4che Modifier Setup
echo ======================================
echo.

REM Change to the project root directory
cd %~dp0..

REM Create the java directory if it doesn't exist
if not exist src\java\ (
    echo Creating Java directory...
    mkdir src\java
)

REM Check if Python is installed and set up the DicomModifier utility
python -c "from src.utils.dcm4che_validator import validate_dcm4che_setup; is_valid, report = validate_dcm4che_setup(); print(report)"

echo.
echo Setup completed. If you see any errors above, please resolve them before using the DICOM tag modification feature.
echo.

pause 