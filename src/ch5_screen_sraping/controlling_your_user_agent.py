import requests
from bs4 import BeautifulSoup

url = "http://whatsmyuseragent.com/"

headers = {
    # 'User-Agent': 'Mozilla/7.0 (Macintosh; Intel Mac OS X 11.32; rv:51.0) Gecko/20100101 Firefox/54.0'
    'User-Agent': 'super-user-agent 007 v0.1'
}

r = requests.get(url, headers=headers)

soup = BeautifulSoup(r.text, "html.parser")
ua = soup.select_one(".user-agent").get_text()

print("YOUR USER AGENT REPORT IS:")
print()
print(ua)
