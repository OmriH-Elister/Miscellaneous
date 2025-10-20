# General
This repository contains miscellaneous scripts I'd written:
1) Temporary-file-cleaner - which is technically not a script but an xml file one can import to a local task scheduler in order to automate routine maintenance work on one's personal computer. The imported file will schedule a collection of batch commands that delete temporary windows files, cleans "deleted files" and performs small fixes and adjustments to the hard drive.
2) brute_apn_hostnames.bat - utilizes a batch one-liner to take a provided username list file as input, loop through each of the usernames and attempt to establish a functional APN connection. It is basically a very simple APN-profile brute force script.
3) WB-CLINAVAEXDRES, Web-Browser’s CLI NAVigator and EXternal DNS RESolver - This python script enables the user to navigate the web browser from the OS's command line (cmd, bash etc.) and is also meant to provide external DNS resolution. By reolving URL's with acustom DNS server it solves situations in which a static DNS server had been set on a device which the user does not have sufficient privileges on for resetting its DNS settings. In such cases, if the DNS server is inefficient in resolving certain URLS (or any of them), the unprivileged user would be unable reset the DNS settings, and therefore unable to use his ordinary web-browser to reach websites due to failed DNS resolutions. This tool bypasses the browser's settings and the device's Globally set DNS server by resolving the URL with a seperate NSLOOKUP process. It then directly crafts and sends its own web request, spins up a local python web server, and relays the web response to said listening python web-server.  The end-result aims to seamlessly surf the web WITH a web browser (no textual web responses), but by controlling it from the command-line and using an external, script-defined DNS server.
It does this by acting as both server and a client, as it both starts a local Webserver to receive and relay its own HTTP responses AND also crafts and sends web requests themselves (after receiving a web URL as input from the user). It then performs its own DNS resolution of the URL with the nslookup tool, crafts and sends the web request with the externally resolved IP address. The web responses reach the listening web-server and are not saved locally, but rather, they are relayed from memory over http/s to the browser (as if thye were its own responses).  Built with implementation support from ChatGPT, based on my original concept and design. Basically, I've built and directed the concept and it coded it for me.
4) produce_report.sh - A Bash script that aggregates text files, runs psychological and linguistic analyses via Fabric, and generates a structured psycho-analysis report for a given user.
5) DirEnum.ps1 is a powershell script that
  a) Receives a folder path from the user as input.
  b) Enumerates said folder recursively (Including all of it's subfolders, their own subfolders, etc.)
  c) For each one of the folder enumerated list its amount of contained folders and files.
  d) Output all the results to a more or less organized file. 
6) DirEnum.bat is a batch file that also provides the same functionality and also works well.   
* Both the DirEnum.ps1 and DirEnum.bat are kind of dumb, because you could easily achieve the same results with 
 the "Get-ChildItem" command (or builtin batch oneliners), but when I had written them I was a Powershell 
 novice, and I'm currently keeping them for reference  as an alternative to the builtin methods 

  
