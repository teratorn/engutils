@echo off

:: skip downloading/setting-up python if we already have python3
python -c "import sys; sys.exit(int(not sys.version_info[0] >= 3))" > NUL 2> NUL && goto :skip_get_python

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
goto :get_inno

:skip_get_python
echo Looks like you already have Python 3 on your system, skipping this step...
pause

:get_inno

:: skip downloading/setting-up innosetup if we already have it
reg query "HKCR\InnoSetupScriptFile\shell\Compile\command" >NUL 2>NUL && goto :skip_get_inno

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
goto :get_py_modules


:skip_get_inno
echo Looks like you already have InnoSetup on your system - skipping this step...
pause


:get_py_modules

cls
echo Now we'll download and install the necessary python modules
echo.
pause

python -m ensurepip || goto :error

python -m pip install --upgrade pip || goto :error

pip3 install pyside2 pyinstaller || goto :error

echo.
echo Successfully downloaded and installed the necessary python modules
pause

::echo.
::echo SUCCESSFULLY INSTALLED EVERYTHING NEEDED FOR EngUtils DEVELOPMENT
::pause
::
::cls
::echo You can close this window now if you wish. If you continue we'll download
::echo a few optional things that make EngUtils development easier.
::echo.
::pause


:: skip downloading/setting-up PyCharm if we already have it
python -c "import winreg;winreg.EnumKey(winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\JetBrains\\PyCharm Community Edition'), 0)" >NUL 2>NUL && goto :skip_get_pycharm

cls
echo Press any key to launch your browser and download PyCharm Community Edition
echo.
echo Accept this download and save the file to the normal Downloads folder
echo.
echo Then switch back to this window to continue the setup process...
echo.
pause

start "" "https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC" || goto :error
timeout /t 2 /nobreak > NUL
echo.
echo Now ONLY AFTER the download has completed successfully...
echo.
pause

echo.
echo Attempting to run the PyCharm setup program with appropriate options...
echo.
echo If prompted by a security warning click the "Run" or "Yes" button.
echo.
echo The installer WILL NOT display a progress window, and may take up to a minute to complete.
echo Please be patient...
timeout /t 2 /nobreak > NUL

powershell -c "$exe = Get-ChildItem $HOME\Downloads\pycharm*.exe | Sort-Object -Descending | Select-Object -First 1 -ExpandProperty Name; Start-Process $HOME\Downloads\$exe -Wait -ArgumentList \""/S\"",\""/CONFIG=pycharm_silent.config\""" || goto :error
goto :get_git_for_windows


:skip_get_pycharm
echo Looks like you already have PyCharm on your system - skipping this step...
pause


:get_git_for_windows

:: skip downloading/setting-up Git for Windows if we already have it
git --help >NUL 2>NUL && goto :skip_get_git_for_windows

cls
echo Press any key to launch your browser and download Git for Windows
echo.
echo Accept this download and save the file to the normal Downloads folder
echo.
echo Then switch back to this window to continue the setup process...
echo.
pause

start "" "https://git-scm.com/download/win"
timeout /t 2 /nobreak > NUL
echo.
echo Now ONLY AFTER the download has completed successfully...
echo.
pause

echo.
echo Attempting to run the Git for Windows setup program with appropriate options...
echo.
echo If prompted by a security warning click the "Run" or "Yes" button.
echo.
timeout /t 2 /nobreak > NUL

powershell -c "$exe = Get-ChildItem $HOME\Downloads\Git*.exe | Sort-Object -Descending | Select-Object -First 1 -ExpandProperty Name; Start-Process $HOME\Downloads\$exe -Wait -ArgumentList \""/SP-\"",\""/SILENT\"",\""/SUPPRESSMSGBOXES\"",\""/NOCANCEL\"",\""/NORESTART\"",\""/CLOSEAPPLICATIONS\"",\""/RESTARTAPPLICATIONS\"",\""/LOADINF=git_setup.inf\""" || goto :error

goto :get_tortoisegit

:skip_get_git_for_windows
echo Looks like you already have Git for Windows on your system - skipping this step...
pause


:get_tortoisegit

:: skip downloading/setting-up TortoiseGit if we already have it
python -c "import winreg, sys, os;sys.exit(int(not os.path.exists(winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\TortoiseGit'), 'SSH')[0])))" >NUL 2>NUL && goto :skip_get_tortoisegit

cls
echo Press any key to launch your browser and download TortoiseGit
echo.
echo Accept this download and save the file to the normal Downloads folder
echo.
echo Then switch back to this window to continue the setup process...
echo.
pause

start "" "https://download.tortoisegit.org/tgit/2.9.0.0/TortoiseGit-2.9.0.0-32bit.msi" || goto :error
timeout /t 2 /nobreak > NUL
echo.
echo Now ONLY AFTER the download has completed successfully...
echo.
pause

echo.
echo Attempting to run the TortoiseGit setup program with appropriate options...
echo.
echo If prompted by a security warning click the "Run" or "Yes" button.
echo.
timeout /t 2 /nobreak > NUL

powershell -c "$exe = Get-ChildItem $HOME\Downloads\TortoiseGit*.msi | Sort-Object -Descending | Select-Object -First 1 -ExpandProperty Name; Start-Process $HOME\Downloads\$exe -Wait -ArgumentList \""/passive\""" || goto :error

goto :done

:skip_get_tortoisegit
echo Looks like you already have TortoiseGit on your system - skipping this step...
pause

:done
echo.
echo.
echo ALL DONE!
pause
exit

:error
echo.
echo ERROR OCCURED - SEE ABOVE
pause
exit
