@echo off
rem -------------------------------------------------------------------------
rem mkkos  Launcher
rem -------------------------------------------------------------------------

if not "%ECHO%" == ""  echo %ECHO%
if "%OS%" == "Windows_NT"  setlocal

set MAIN_CLASS=org.dcm4che3.tool.mkkos.MkKOS
set MAIN_JAR=dcm4che-tool-mkkos-5.33.1.jar

set DIRNAME=.\
if "%OS%" == "Windows_NT" set DIRNAME=%~dp0%

rem Read all command line arguments

set ARGS=
:loop
if [%1] == [] goto end
        set ARGS=%ARGS% %1
        shift
        goto loop
:end

if not "%DCM4CHE_HOME%" == "" goto HAVE_DCM4CHE_HOME

set DCM4CHE_HOME=%DIRNAME%..

:HAVE_DCM4CHE_HOME

if not "%JAVA_HOME%" == "" goto HAVE_JAVA_HOME

set JAVA=java

goto SKIP_SET_JAVA_HOME

:HAVE_JAVA_HOME

set JAVA=%JAVA_HOME%\bin\java

:SKIP_SET_JAVA_HOME

set CP=%DCM4CHE_HOME%\etc\mkkos\
set CP=%CP%;%DCM4CHE_HOME%\lib\%MAIN_JAR%
set CP=%CP%;%DCM4CHE_HOME%\lib\dcm4che-core-5.33.1.jar
set CP=%CP%;%DCM4CHE_HOME%\lib\dcm4che-tool-common-5.33.1.jar
set CP=%CP%;%DCM4CHE_HOME%\lib\slf4j-api-2.0.16.jar
set CP=%CP%;%DCM4CHE_HOME%\lib\logback-core-1.5.12.jar
set CP=%CP%;%DCM4CHE_HOME%\lib\logback-classic-1.5.12.jar
set CP=%CP%;%DCM4CHE_HOME%\lib\commons-cli-1.9.0.jar

"%JAVA%" %JAVA_OPTS% -cp "%CP%" %MAIN_CLASS% %ARGS%
