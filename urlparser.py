import urllib.request
import urllib.error
import bs4


def get_title(url):
    try:
        page = urllib.request.urlopen(url)
        bs = bs4.BeautifulSoup(page, "html.parser")
        if bs.title:
            return bs.title.string.strip()
    except:
        print('bazdmeg')
        pass
