#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re

def debug(msg, ctx=''):
    print(f"dbg: {ctx}{msg}")

def paren(text):
    return f"({text})"

def strip_margin(text):
    return re.sub(r'\n[ \t]*\|', '\n', text).strip()
