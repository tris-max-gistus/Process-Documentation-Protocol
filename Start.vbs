' Windows launcher: starts Process Log with no console window.
' If Python's windowless runner is missing, falls back to a visible window
' (app\start.bat) so any problem is readable.
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
here = fso.GetParentFolderName(WScript.ScriptFullName)
On Error Resume Next
sh.Run "pythonw """ & here & "\app\start.py""", 0, False
If Err.Number <> 0 Then
    Err.Clear
    sh.Run """" & here & "\app\start.bat""", 1, False
End If
