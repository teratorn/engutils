import EngUtils

from EngUtils.ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

import shutil
import glob
import os.path
import sys
try:
    import py2exe
except ImportError:
    pass

pkgDir = os.path.dirname(EngUtils.__file__)
with open(os.path.join(pkgDir, 'version.txt'), 'r') as f:
    versionString = f.read().strip()

setup(name="EngUtils",
      version=versionString,
      description="GUI calculation screens for various Engineering functions",
      author="Eric P. Mangold",
      author_email="teratorn /AT/ zoho /DOT/ com",
      packages=['EngUtils'],
      windows=[{'script' : 'main.py',
                'icon_resources' : [(1, 'icon.ico')]
                }],
      options = {"py2exe": {"skip_archive":1}},

      # not respected by py2exe for some reason
      package_data={'EngUtils' : ['icon.png',
                                  'version.txt']},
      scripts=['bin/engutils'],
      install_requires=['PySide']
      )

if sys.argv[1] == 'py2exe':
    for name in glob.glob('EngUtils/*.py'):
        shutil.copyfile(name, os.path.join('dist', name))

    icon = 'EngUtils/icon.png'
    shutil.copyfile(icon, os.path.join('dist', icon))

    icon = 'icon.ico'
    shutil.copyfile(icon, os.path.join('dist', icon))

    lic = 'LICENSE.txt'
    shutil.copyfile(lic, os.path.join('dist', lic))

    version_file = 'EngUtils/version.txt'
    shutil.copyfile(version_file, os.path.join('dist', version_file))

    shutil.move('dist/main.exe', 'dist/EngUtils.exe')
    shutil.copyfile('msvcp90.dll', 'dist/msvcp90.dll')

