@echo off

:: skip downloading/setting-up python if we already have python3
python -c "import sys; sys.exit(int(not sys.version_info[0] >= 3))" > NUL 2> NUL && goto :get_inno

echo Press any key to launch your browser and download python-3.7.6.exe
echo.
echo Accept this download and save the file to the normal Downloads folder
echo.
echo Then switch back to this window to continue the setup process...
echo.
pause

start "" https://www.python.org/ftp/python/3.7.6/python-3.7.6.exe || goto :error
timeout /t 2 /nobreak > NUL
echo.
echo Now ONLY AFTER the download has completed successfully...
echo.
pause

echo.
echo.
echo Attempting to run the python setup program with appropriate options...
echo.
echo If prompted by a security warning click the "Run" button.
timeout /t 2 /nobreak > NUL

powershell -c "$py = Get-ChildItem $HOME\Downloads\python-3*.exe | Sort-Object -Descending | Select-Object -First 1 -ExpandProperty Name; Start-Process $HOME\Downloads\$py -Wait -ArgumentList \""/passive\"",\""InstallAllUsers=0\"",\""AssociateFiles=1\"",\""CompileAll=1\"",\""PrependPath=1\"",\""Include_launcher=1\"",\""InstallLauncherAllUsers=0\"",\""Include_pip=1\"",\""Include_tcltk=0\"",\""Include_test=0\""" || goto :error

:: Reload PATH from registry so that we can actually call the newly installed python.exe
:: https://stackoverflow.com/a/39962543

:: Get System PATH
for /f "tokens=3*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do set syspath=%%A%%B

:: Get User Path
for /f "tokens=3*" %%A in ('reg query "HKCU\Environment" /v Path') do set userpath=%%A%%B

:: Set Refreshed Path
set PATH=%userpath%;%syspath%


:get_inno

:: skip downloading/setting-up innosetup if we already have it
reg query "HKCR\InnoSetupScriptFile\shell\Compile\command" >NUL 2>NUL && goto :get_py_modules

cls
echo Press any key to launch your browser and download innosetup
echo.
echo Accept this download and save the file to the normal Downloads folder
echo.
echo Then switch back to this window to continue the setup process...
echo.
pause

start "" http://www.jrsoftware.org/download.php/is.exe?site=1 || goto :error
timeout /t 2 /nobreak > NUL
echo.
echo Now ONLY AFTER the download has completed successfully...
echo.
pause

echo.
echo Attempting to run the innosetup setup program with appropriate options...
echo.
echo If prompted by a security warning click the "Run" button.
timeout /t 2 /nobreak > NUL

powershell -c "$inno = Get-ChildItem $HOME\Downloads\innosetup*.exe | Sort-Object -Descending | Select-Object -First 1 -ExpandProperty Name; Start-Process $HOME\Downloads\$inno -Wait -ArgumentList \""/SILENT\"",\""/SUPPRESSMSGBOXES\"",\""/CURRENTUSER\"",\""/NOCANCEL\"",\""/NORESTART\"",\""/NOCLOSEAPPLICATIONS\"",\""/NORESTARTAPPLICATIONS\"",\""/LANG=english\""" || goto :error


:get_py_modules

cls
echo Now we'll download and install the necessary python modules
echo.
pause

python -m ensurepip || goto :error

python -m pip install --upgrade pip || goto :error

pip3 install pyside2 pyinstaller || goto :error

echo.
echo SUCCESSFULLY INSTALLED EVERYTHING
pause
exit

:error
echo.
echo ERROR OCCURED - SEE ABOVE
pause
exit
