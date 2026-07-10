set CURRENT_DATA_STRING=%date:~6,4%%date:~0,2%%date:~3,2%
echo CURRENT_DATA_STRING=%CURRENT_DATA_STRING%
cd /d %~dp0
copy track_test_config_fp3-7_clinic.ini .\config_backup\track_test_config_fp3-7_clinic%CURRENT_DATA_STRING%.ini /Y 



