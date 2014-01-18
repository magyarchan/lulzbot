import urllib.request
import urllib.error
import bs4


def get_title(url):
    try:
        page = urllib.request.urlopen(url)
        bs = bs4.BeautifulSoup(page)
        return bs.title.string
    # TODO: dobodhat itt mas exception?
    except (urllib.error.URLError, ValueError):
        pass