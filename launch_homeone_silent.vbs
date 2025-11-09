Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Obtient le dossier du script
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
strPowerShellScript = strScriptPath & "\launch_homeone.ps1"

' Lance PowerShell en mode invisible
objShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & strPowerShellScript & """", 0, False

Set objShell = Nothing
Set objFSO = Nothing
