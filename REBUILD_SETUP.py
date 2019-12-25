#!/usr/bin/env python3
import os
import os.path
import sys
import subprocess
import shutil
import glob

try:
    import _winreg as winreg
except ImportError:
    import winreg

thisFile = sys.argv[0]
try:
    thisFile = __file__
except NameError:
    pass

thisDir = os.path.abspath(os.path.dirname(thisFile))
os.chdir(thisDir)

def exit(code):
    print()
    print("Press Enter to continue...")
    input() # wait for Enter key press
    sys.exit(code)

try:
    subprocess.check_call(['pyinstaller',
        '-y',
        #'-d', 'noarchive', # doesn't appear to do anything...
        '-i', 'icon.ico',
        '-n', 'EngineeringUtilities',
        '--noconsole',
        '--add-data', 'EngUtils\\version.txt;EngUtils',
        '--add-data', 'EngUtils\\icon.png;EngUtils',
        'main.py'])
except subprocess.CalledProcessError:
    print("Error running pyinstaller")
    print("Failed to build installer...")
    exit(1)

#for name in glob.glob('EngUtils/*.py'):
#    shutil.copyfile(name, os.path.join('dist', name))

try:
    # copy some stuff to dist directory
    eng = 'EngineeringUtilities'

    #icon = 'EngUtils/icon.png'
    #shutil.copyfile(icon, os.path.join('dist', eng, icon))

    #version_file = 'EngUtils/version.txt'
    #shutil.copyfile(version_file, os.path.join('dist', eng, version_file))

    icon = 'icon.ico'
    shutil.copyfile(icon, os.path.join('dist', eng, icon))

    lic = 'LICENSE.txt'
    shutil.copyfile(lic, os.path.join('dist', eng, lic))


    # delete some large extranious files from dist directory
    # that are apparently not needed for EngUtils
    names = (
            '_bz2.pyd',
            '_hashlib.pyd',
            '_lzma.pyd',
            '_socket.pyd',
            '_ssl.pyd',

            'libGLESv2.dll',

            'libcrypto-1_1.dll',
            'libssl-1_1.dll',
            'Qt5DBus.dll',
            'Qt5QmlModels.dll',
            'Qt5Quick.dll',
            'Qt5Svg.dll',
            'Qt5WebSockets.dll',
            'Qt5VirtualKeyboard.dll',

            'ucrtbase.dll',
            'unicodedata.pyd',

            'PySide2/d3dcompiler_47.dll',
            'PySide2/libEGL.dll',
            'PySide2/libGLESv2.dll',
            'PySide2/opengl32sw.dll',
            'PySide2/QtNetwork.pyd',

            'PySide2/plugins/platforms/qminimal.dll',
            'PySide2/plugins/platforms/qoffscreen.dll',
            'PySide2/plugins/platforms/qwebgl.dll',
            )
    for name in names:
        pth = os.path.join('dist', eng, name)
        if os.path.exists(pth):
            os.remove(pth)

    dirs = (
            'PySide2/translations',
            'PySide2/plugins/bearer',
            'PySide2/plugins/iconengines',
            'PySide2/plugins/imageformats',
            'PySide2/plugins/platforminputcontexts',
            'PySide2/plugins/platformthemes',
            'PySide2/plugins/styles',
            )
    for name in dirs:
        pth = os.path.join('dist', eng, name)
        if os.path.exists(pth):
            shutil.rmtree(pth)

except:
    import traceback
    traceback.print_exc()
    exit(1)

# Now locate the InnoSetup compiler

try:
    innoCmd = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, "InnoSetupScriptFile\shell\Compile\command")
except WindowsError:
    print()
    print("ERROR: Unable to locate your Inno Setup installation in the registry!")
    print("Have you installed Inno Setup? http://www.jrsoftware.org/isdl.php")
    exit(1)

innoCmd = innoCmd.replace("\"%1\"", "setup.iss")
try:
    subprocess.check_call(innoCmd, shell=True)
except subprocess.CalledProcessError:
    print()
    print("ERROR running Inno Setup")
    print("Failed to build installer...")
    exit(1)

print()
print()
print()
print("SUCCESS building EngineeringUtilitiesSetup.exe !!!")
print()
print("Be sure that you edited EngUtils\\version.txt to increment the version number.")
print("If not, go do that now, and re-run this program.")
exit(0)
