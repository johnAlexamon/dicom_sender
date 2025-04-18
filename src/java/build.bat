@echo off
setlocal

REM Get the current directory 
set JAVA_DIR=%~dp0
set SOURCE_FILE=%JAVA_DIR%DicomModifier.java

REM Get the lib directory from the environment or use a default
set LIB_DIR=%JAVA_DIR%..\..\lib\dcm4che\lib

REM Check if the lib directory exists
if not exist "%LIB_DIR%" (
    echo Error: Library directory %LIB_DIR% not found.
    exit /b 1
)

REM Check if the source file exists
if not exist "%SOURCE_FILE%" (
    echo Error: Source file %SOURCE_FILE% not found.
    exit /b 1
)

REM Compile using wildcard classpath
echo Building DicomModifier...
javac -cp "%LIB_DIR%\*" "%SOURCE_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo Compilation failed.
    exit /b 1
) else (
    echo Compilation successful. DicomModifier.class created.
)

exit /b 0 