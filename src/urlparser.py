#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import urllib.request
import urllib.error
import bs4


def get_title(url):
    page = {}
    try:
        request = urllib.request.Request(url, method='HEAD')
        head = urllib.request.urlopen(request, timeout = 3)
        if head.code == 200:
            page = urllib.request.urlopen(url)
            try:
                bs = bs4.BeautifulSoup(page, "html.parser")
                if bs.title:
                    return bs.title.string.strip()
            except Exception as e:
                error = getattr(e, 'reason', e)
                print(str(error))
                return ''
        else:
            return ''
    except Exception as e:
        print('bazdmeg: ' + str(e))
        return ''
