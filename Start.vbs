' Launches the LLM Usage Logger with no visible console window.
' Double-click this file (or a shortcut to it) to start the app silently;
' your browser will open once it's ready. If something goes wrong, a
' small error window will appear and details are saved to launch_log.txt
' in the app folder. Use app\start.bat instead if you need to see setup output.

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' One-time convenience: plant a desktop shortcut so future launches don't
' require opening this folder at all. Tracked by a marker file in app\ so
' it only happens once per clone; delete the marker to redo it. Best-effort
' -- if this fails for any reason (permissions, etc.) it's silently skipped
' and the app still launches normally below.
strMarker = strPath & "\app\.shortcut_created"
If objFSO.FolderExists(strPath & "\app") And Not objFSO.FileExists(strMarker) Then
    On Error Resume Next
    strSystemRoot = objShell.ExpandEnvironmentStrings("%SystemRoot%")
    strDesktop = objShell.SpecialFolders("Desktop")
    Set objShortcut = objShell.CreateShortcut(strDesktop & "\Process Logger.lnk")
    objShortcut.TargetPath = strPath & "\Start.vbs"
    objShortcut.WorkingDirectory = strPath
    objShortcut.IconLocation = strSystemRoot & "\System32\shell32.dll,167"
    objShortcut.Description = "Launch Process Logger"
    objShortcut.Save
    If Err.Number = 0 Then
        Set objMarker = objFSO.CreateTextFile(strMarker, True)
        objMarker.Close
    End If
    Err.Clear
    On Error Goto 0
End If

objShell.CurrentDirectory = strPath
objShell.Run "pythonw """ & strPath & "\app\start.py""", 0, False
