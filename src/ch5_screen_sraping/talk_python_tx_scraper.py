import collections
import requests
from xml.etree import ElementTree
from bs4 import BeautifulSoup

Page = collections.namedtuple('Page', 'url title paragraphs')
Paragraph = collections.namedtuple('Paragraph', 'text seconds')


def main():
    tx_urls = get_transcript_urls()
    pages = download_transcript_pages(tx_urls[:5])
    show_pages(pages)


def show_pages(pages):
    for p in pages:
        print(p.title)
        print("* {}".format(p.url))
        print("* {:,} paragraphs".format(len(p.paragraphs)))
        print(" 1. {}".format(p.paragraphs[0].text))
        print()


def download_transcript_pages(tx_urls):
    pages = []

    for url in tx_urls:
        page = build_page_from_url(url)
        pages.append(page)

    return pages


def build_page_from_url(url):
    print("Downloading {}...".format(url), flush=True)
    resp = requests.get(url)
    html = resp.text

    soup = BeautifulSoup(html, 'lxml')

    title = clean_line(soup.find('h1').get_text())

    paragraphs = [
        Paragraph(clean_line(p.get_text()), int(p['seconds']))
        for p in soup.select(".transcript-segment")]

    return Page(url, title, paragraphs)


def get_transcript_urls():
    sitemap_url = 'https://talkpython.fm/sitemap.xml'
    resp = requests.get(sitemap_url)
    if resp.status_code != 200:
        print("Cannot get sitemap, {} {}".format(resp.status_code, resp.text))
        return []

    xml_text = resp.text.replace('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', '')
    dom = ElementTree.fromstring(xml_text)

    tx_urls = [
        n.text
        for n in dom.findall('url/loc')
        if n.text.find('/episodes/transcript') > 0
        ]

    return tx_urls


def clean_line(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    size = len(text) + 1
    while size > len(text):
        size = len(text)
        text = text.replace('  ', ' ')
    return text.strip()


if __name__ == '__main__':
    main()
