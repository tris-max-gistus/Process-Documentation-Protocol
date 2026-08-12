' Runs the LLM Usage Logger export step with no visible console window.
' Double-click this file to create a submission zip (it lands in this same
' "submit" folder). A confirmation (or error) window will appear when it's
' done - this can take a few seconds. Details are also logged to
' ..\app\launch_log.txt.

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
strRoot = objFSO.GetParentFolderName(strPath)

pythonwPath = strRoot & "\app\venv\Scripts\pythonw.exe"
exportScript = strRoot & "\app\export.py"

If Not objFSO.FileExists(pythonwPath) Then
    MsgBox "The app hasn't been started yet, so there's nothing to export." & vbCrLf & vbCrLf & _
           "Please run Start.vbs first, use the app for a session, then try Export again.", _
           vbExclamation, "LLM Usage Logger - Export"
    WScript.Quit 1
End If

objShell.CurrentDirectory = strRoot
objShell.Run """" & pythonwPath & """ """ & exportScript & """", 0, False
