import requests


def main():
    url = 'https://talkpython.fm/'

    resp = requests.get(url)

    if resp.status_code != 200:
        print("Error requesting URL, {}".format(resp.status_code))
        return

    print(resp.text[:500])


if __name__ == '__main__':
    main()
