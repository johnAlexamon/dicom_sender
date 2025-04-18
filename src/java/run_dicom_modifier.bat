@echo off
setlocal

REM Get the current directory 
set JAVA_DIR=%~dp0

REM Get the lib directory from the environment or use a default
set LIB_DIR=%JAVA_DIR%..\..\lib\dcm4che\lib

REM Check if the lib directory exists
if not exist "%LIB_DIR%" (
    echo Error: Library directory %LIB_DIR% not found.
    exit /b 1
)

REM Run the DicomModifier with wildcard classpath
java -cp "%JAVA_DIR%;%LIB_DIR%\*" DicomModifier %*

exit /b %ERRORLEVEL% 