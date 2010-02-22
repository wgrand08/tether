#cs
    Copyright 2009:
        Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#ce

If FileExists("C:\Python26\python.exe") Then
	
    $placeholder = True
	
Else
    MsgBox(4096,"MoonPy installer", "Python2.6 is not installed, starting install process")
	;RunWait("explorer http://www.python.org/ftp/python/2.6.4/python-2.6.4.msi")
	RunWait("msiexec -i http://www.python.org/ftp/python/2.6.4/python-2.6.4.msi")
EndIf
ShellExecuteWait(".\moon.py")
