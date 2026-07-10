@echo off
setlocal enabledelayedexpansion
REM Set the IP address or hostname of the target computer
set "target1=192.168.30.9"
REM Set the interval time for checking (in seconds)
set "interval=1"
REM Output a message indicating the start of the continuous check
echo Continuously checking communication with %target1%...
echo Press Ctrl+C to stop the check.
REM Create or clear the log file (with a timestamped header for clarity)
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=:." %%a in ('time /t') do (set mytime=%%a-%%b)
set "startTimestamp=%mydate% %mytime:~0,8%"
echo Log started at %startTimestamp% > network_check.log
 
:checkLoop
REM Get the current timestamp
for /f "tokens=2 delims==" %%i in ('"wmic os get localdatetime /value"') do set datetime=%%i
set timestamp=!datetime:~0,4!-!datetime:~4,2!-!datetime:~6,2! !datetime:~8,2!:!datetime:~10,2!:!datetime:~12,2!
REM Check the target computer
ping -n 1 %target1% | findstr /i "TTL=" >nul
if !errorlevel! equ 0 (
    echo !timestamp!, %target1% is online >> network_check.log
    echo !timestamp!, %target1% is online
) else (
    echo !timestamp!, %target1% is offline >> network_check.log
    echo !timestamp!, %target1% is offline
)

REM Wait for the specified interval
timeout /t %interval% /nobreak

REM Go back to the loop
goto checkLoop