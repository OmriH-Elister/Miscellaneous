@echo off 
:main
dir /d > TEMPfile1.txt
set /p LocDirList=<TEMPfile1.txt
del TEMPfile1.txt
goto :main2
:main2 
if %LocDirList% == " " 
goto :eof
else:
echo %LocDirList% >> LocDirList.txt
for %%f in %LocDirList% do goto :loop
:loop
cd %%f 
dir /d >TEMPfile2.txt
set /p LocDirList=<TEMPfile2
del TEMPfile2.txt
goto :main2 
:eof