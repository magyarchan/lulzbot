import urllib.request
import urllib.error
import bs4


def get_title(url):
    try:
        request = urllib.request.Request(url, method='HEAD')
        head = urllib.request.urlopen(request, timeout = 3)
        if head.code == 200:
            page = urllib.request.urlopen(url)
            bs = bs4.BeautifulSoup(page, "html.parser")
            if bs.title:
                return bs.title.string.strip()
        else:
            return ''
    except Exception as e:
        print('bazdmeg: ' + e.reason)
        return ''
