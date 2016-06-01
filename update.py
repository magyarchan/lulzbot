#! /usr/bin/env python
#
# update script for ufb
#
# jaksi

"""
ufb update script-je
"""

import sys
import urllib
import subprocess
import time
import os
import commands
import shutil

time.sleep(5)
os.rename(u'bot.py', u'bot.py.bak')
os.rename(u'bot.py.new', u'bot.py')
subprocess.Popen([u'python', u'bot.py'])
