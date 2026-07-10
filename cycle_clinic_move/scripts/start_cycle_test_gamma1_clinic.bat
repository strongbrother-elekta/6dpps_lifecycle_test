set CURRENT_DATA_STRING=%date:~6,4%%date:~0,2%%date:~3,2%
set CURRENT_TIME_STRING=%time:~3,2%%time:~6,2%
echo CURRENT_DATA_STRING=%CURRENT_DATA_STRING%

cd %~dp0

setlocal

set "PROCESS_NAME=python.exe"

:start
choice /t 5 /d y /n >nul
tasklist | find /i "%PROCESS_NAME%" > nul

if %errorlevel%==0 (
    echo "%CURRENT_TIME_STRING%"
) else (
	cd ..
	python -X faulthandler -m pytest -p no:faulthandler -s --target-host=192.168.150.9 pps_cycle_test_gamma1_clinic.py
    echo "pytest script........"
)
goto start


pause