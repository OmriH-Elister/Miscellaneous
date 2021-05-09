@echo-off
dir /d | set LocDirList
:main 
if @LocDirList != " "
	do
		echo @LocDirList >> locDirList.txt && for %%i in @LocDirList: 
			do
				cd %%i && dir /d > @LocDirList
				goto :main
	else
		goto :eof

:eof