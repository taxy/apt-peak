#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from glob import glob

setup(name="apt-peak",
      version="1.0",
      description="Apt peak project",
      author="Kollár Endre",
      author_email="taxy443@gmail.com",
      py_modules=['peak_common'],
      scripts=['package_peak','package_debug','peak_tree','gapt-peak'],
      data_files = [('share/apt-peak/glade',
                     ['apt-peak.glade'])]
      )
