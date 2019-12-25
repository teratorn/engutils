#!/usr/bin/env python3
import EngUtils

try:
    from setuptools import setup
except ImportError:
    # was used for older Python's where setuptools
    # wasn't readily available by default
    from EngUtils.ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import shutil
import glob
import os.path
import sys

pkgDir = os.path.dirname(EngUtils.__file__)
with open(os.path.join(pkgDir, 'version.txt'), 'r') as f:
    versionString = f.read().strip()

setup(name="EngineeringUtilities",
      version=versionString,
      description="GUI calculation screens for various Engineering functions",
      author="Eric P. Mangold",
      author_email="teratorn /AT/ zoho /DOT/ com",
      packages=['EngUtils'],
      windows=[{'script' : 'main.py',
                'icon_resources' : [(1, 'icon.ico')]
                }],

      package_data={'EngUtils' : ['icon.png',
                                  'version.txt']},
      scripts=['bin/engutils'],
      install_requires=['pyside2']
      )
