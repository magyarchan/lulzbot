import json
import urllib.request
import urllib.parse


def search(query):
    params = {'q': query,
              'o': 'json',
              'kp': '-1',
              'no_redirect': '1',
              'no_html': '1',
              'd': '1'}
    url = 'http://api.duckduckgo.com/?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')
    response.close()
    results = json.loads(data)
    if results['Answer']:
        return results['Answer']
    elif results['AbstractText']:
        return results['AbstractText'] + ' (' + results['AbstractURL'] + ')'
    elif results['Definition']:
        return results['Definition'] + ' (' + results['DefinitionURL'] + ')'
    elif len(results['RelatedTopics']):
        return results['RelatedTopics'][0]['Text'] + ' (' + results['RelatedTopics'][0]['FirstURL'] + ')'
    elif results['Redirect']:
        return results['Redirect']
    elif query[0] != '\\':
        return search('\\' + query)
    else:
        return 'Nincs találat.'