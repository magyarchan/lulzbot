#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#
# update script for ufb
#
# jaksi

"""
ufb update script-je
"""

import subprocess
import time
import os

time.sleep(5)
os.rename(u'bot.py', u'bot.py.bak')
os.rename(u'bot.py.new', u'bot.py')
subprocess.Popen([u'python', u'bot.py'])
