@echo off
set /p APN=What is the APN's name?
for /f %%i in ('type usernames.txt') do (netsh mbn add profile interface="Cellular" Name="$APN" user=%i%) && sleep 20 
