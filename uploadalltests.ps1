$desthosts = @("MA-TAB0010", "MA-TAB0011", "MA-TAB0050", "MA-TAB0094","MA-TAB0107", "MA-TAB0108", "MA-TAB0109", "MA-TAB0110", "MA-TAB0116", "MA-TAB0117", "MA-TAB0118", "MA-TAB0139", "MB-TAB0173", "MB-TAB0175", "MB-TAB0179", "MB-TAB0176", "MB-TAB0177", "MB-TAB0178", "MB-TAB0180", "MB-TAB0181")
$Ftime = (Get-Date).Tostring("HH:mm")
$Ftime2 = "value="+'"'+$ftime +'"'+' />'
foreach ($rem in $desthosts){ 
	$path1 = "\\$rem\c$\program files (x86)\MotorolaSolutions\DvrManager\DvrManager.Host.exe"
	$path2 = "\\$rem\c$\program files (x86)\MotorolaSolutions\DvrManager\"
	Invoke-command -command { cmd.exe /c sc \\$rem start WinRM } ` # activates winrm on remote host
	set-location $path2 ;`
	$content = get-content DvrManager*.config  ; `  # Then it reads the configuration file and stores it in a variable.
	$content2 = $content -replace 'value="20:00" />', $Ftime2 ; ` # Then it edits the variable to replace the designated time of 20:00 with the current time+10 min
	set-content -path DvrManager*.config -value $content2 ; `  # Finally, it pastes the edited text back into the file instead of the old text. 
	#Restart the DVR service and run the upload application
	write-output "Restarting the dvr service now..." ; `
	Invoke-Command  -Command { cmd.exe /c sc \\$rem stop 1_dvrmanager } ; `
	Invoke-Command  -Command { cmd.exe /c sc \\$rem start 1_dvrmanager } ; `
	write-host "The test-videos are being uploaded as we speak! This is very exciting!" ; `
	start-process -filepath $path1  ;`
	start-sleep -seconds 240  ; `
	stop-process -name "DvrManager.Host" ;`
	Write-output "cleaning up configuration file..."  ; `
	set-content -path  "DvrManager.Host.exe.config" -value $content ; `
	set-location $home\desktop\main_ts_screen\
	write-output "Restarting the dvr service now... again... " ; `
	Invoke-Command  -Command { cmd.exe /c sc \\$rem stop 1_dvrmanager } ; `
	Invoke-Command  -Command { cmd.exe /c sc \\$rem start 1_dvrmanager } ; `
	}