import requests
from xml.etree import ElementTree
import collections
from dateutil.parser import parse

Episode = collections.namedtuple('Episode', 'title link pubdate')


def main():
    dom = get_xml_dom('https://talkpython.fm/rss')
    episodes = get_episodes(dom)

    for idx, e in enumerate(episodes[:5]):
        print('{}. {}'.format(idx, e.title))


def get_xml_dom(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        return None

    dom = ElementTree.fromstring(resp.text)
    return dom


def get_episodes(dom):
    item_nodes = dom.findall('channel/item')

    episodes = [
        Episode(
            n.find('title').text,
            n.find('link').text,
            parse(n.find('pubDate').text)
        )
        for n in item_nodes
        ]

    return sorted(episodes, key=lambda e: e.pubdate)


if __name__ == '__main__':
    main()
