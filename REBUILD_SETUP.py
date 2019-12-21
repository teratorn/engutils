import os
import os.path
import sys
import subprocess
import _winreg

thisFile = sys.argv[0]
try:
    thisFile = __file__
except NameError:
    pass

thisDir = os.path.abspath(os.path.dirname(thisFile))
os.chdir(thisDir)

def exit(code):
    print
    print "Press Enter to continue..."
    raw_input() # wait for Enter key press
    sys.exit(code)

try:
    subprocess.check_call([sys.executable, 'setup.py', 'py2exe'])

except subprocess.CalledProcessError:
    print "Error running py2exe"
    print "Failed to build installer..."
    exit(1)

# Now locate the InnoSetup compiler

try:
    innoCmd = _winreg.QueryValue(_winreg.HKEY_CLASSES_ROOT, "InnoSetupScriptFile\shell\Compile\command")
except WindowsError:
    print
    print "ERROR: Unable to locate your Inno Setup installation in the registry!"
    print "Have you installed Inno Setup? http://www.jrsoftware.org/isdl.php"
    exit(1)

innoCmd = innoCmd.replace("\"%1\"", "setup.iss")
try:
    subprocess.check_call(innoCmd, shell=True)
except subprocess.CalledProcessError:
    print
    print "ERROR running Inno Setup"
    print "Failed to build installer..."
    exit(1)

print
print
print
print "SUCCESS building Setup Eng Utils.exe !!!"
print
print "Be sure that you edited version.txt to indicate a new version."
print "If not go do that now and re-run this program"
exit(0)
