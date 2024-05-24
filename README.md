# General
This repository contains miscellaneous scripts I'd written:
1) Temporary-file-cleaner - which is technically not a script but an xml file one can import to a local task scheduler in order to automate routine maintenance work on one's personal computer. The imported file will schedule a collection of batch commands that delete temporary windows files, cleans "deleted files" and performs small fixes and adjustments to the hard drive.
2) brute_apn_hostnames.bat - utilizes a batch one-liner to take a provided username list file as input, loop through each of the usernames and attempt to establish a functional APN connection. It is basically a very simple APN-profile brute force script.

* Both the DirEnum.ps1 and DirEnum.bat are kind of dumb, because you could easily achieve the same results with 
 the "Get-ChildItem" command (or builtin batch oneliners), but when I had written them I was a Powershell 
 novice, and I'm currently keeping them for reference as an alternative to the builtin methods 
- DirEnum.ps1 is a powershell script that
  1) Receives a folder path from the user as input.
  2) Enumerates said folder recursively (Including all of it's subfolders, their own subfolders, etc.)
  3) For each one of the folder enumerated list its amount of contained folders and files.
  4) Output all the results to a more or less organized file. 
- DirEnum.bat is a batch file that also provides the same functionality and also works well. 

