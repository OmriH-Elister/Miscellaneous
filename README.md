# General
This repository contains miscellaneous scripts I'd written:
1) Temporary-file-cleaner - which is technically not a script but an xml file one can import to a local task scheduler in order to automate routine maintenance work on one's personal computer. The imported file will schedule a collection of batch commands that delete temporary windows files, cleans "deleted files" and performs small fixes and adjustments to the hard drive.
2) brute_apn_hostnames.bat - utilizes a batch one-liner to take a provided username list file as input, loop through each of the usernames and attempt to establish a functional APN connection. It is basically a very simple APN-profile brute force script.
3) PyResWeBrowse.py - this python script is meant to provide a solution for situations in which a static DNS server had been set on a device which the user does not have sufficient privileges on to reset DNS settings. In such cases, if the DNS server is inefficient in resolving certain URLS (or any of them), the unprivileged user would be unable reset the DNS settings, and therefore unable to use his ordinary web-browser to reach websites due to failed DNS resolutions. This script bypasses the browser's settings and the device's set DNS server by resolving the URL with a seperate NSLOOKUP process. It then directly crafts and sends the web request, automatically saving and opening the web response with an ordinary browser.
The end-result aims to seamlessly surf the web WITH a web browser (no textual web responses), but by controlling it from the command-line and using an external script-defined DNS server.
It does this by acting as both server and client, as it both starts a local Webserver to intercept its own web requests AND also crafts and sends said web requests themselves (after receiving a web URL as input from the user). It then performs its own DNS resolution of the URL with the nslookup tool, crafts and sends the web request with the resultant IP address, saves its respective web response as and html file and opens said file utilizing a web browser. 
* Both the DirEnum.ps1 and DirEnum.bat are kind of dumb, because you could easily achieve the same results with 
 the "Get-ChildItem" command (or builtin batch oneliners), but when I had written them I was a Powershell 
 novice, and I'm currently keeping them for reference as an alternative to the builtin methods 
- DirEnum.ps1 is a powershell script that
  1) Receives a folder path from the user as input.
  2) Enumerates said folder recursively (Including all of it's subfolders, their own subfolders, etc.)
  3) For each one of the folder enumerated list its amount of contained folders and files.
  4) Output all the results to a more or less organized file. 
- DirEnum.bat is a batch file that also provides the same functionality and also works well. 
  
