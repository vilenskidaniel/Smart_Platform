Option Explicit

Dim shell, fso, scriptDir, ps1Path, command, idx, arg, forwardedArgs

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
ps1Path = scriptDir & "\Launch-SmartPlatformShell.ps1"
forwardedArgs = ""

For idx = 0 To WScript.Arguments.Count - 1
    arg = WScript.Arguments(idx)
    arg = Replace(arg, """", """""")
    forwardedArgs = forwardedArgs & " """ & arg & """"
Next

command = "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & ps1Path & """" & forwardedArgs
shell.Run command, 0, False