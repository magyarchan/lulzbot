import urllib.request
import urllib.error
import bs4


def get_title(url):
    try:
        page = urllib.request.urlopen(url)
        bs = bs4.BeautifulSoup(page)
        if bs.title:
            return bs.title.string.strip()
    except:
        pass
