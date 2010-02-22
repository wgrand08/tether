#requireadmin
If FileExists("C:\Python26\python.exe") Then
	
    $placeholder = True
	
Else
    MsgBox(4096,"MoonPy installer", "Python2.6 is not installed, starting install process")
	ShellExecuteWait("explorer http://www.python.org/ftp/python/2.6.4/python-2.6.4.msi")
EndIf
ShellExecuteWait(".\moon.py")