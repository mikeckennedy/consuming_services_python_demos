import datetime
import collections
import json
import urllib.request
import urllib.error
import sys

Post = collections.namedtuple("Post", 'id title content published view_count')

base_url = 'http://consumer_services_api.talkpython.fm/api/restricted/blog/'
user = 'kennedy'
password = 'super_lockdown'


def register_auth():
    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, base_url, user, password)

    authenticated_handler = urllib.request.HTTPBasicAuthHandler(password_manager)
    opener = urllib.request.build_opener(authenticated_handler)

    urllib.request.install_opener(opener)


def main():
    print("Blog explorer (Python 3 builtins version, with auth)")
    if sys.version_info.major == 2:
        print("This sample requires at least Python 3, exiting...")
        return

    register_auth()

    while True:
        action = input('What to do with this blog api? [l]ist, [a]dd, [u]pdate, [d]elete, e[x]it: ')
        if action == 'x':
            print("Exiting...")
            break
        if action == 'l':
            posts = get_posts()
            show_posts(posts)
        if action == 'a':
            add_post()
        if action == 'u':
            update_post()
        if action == 'd':
            delete_post()


def show_posts(posts):
    if not posts:
        print("Sorry, no posts to show.")
        return

    print("------------------------------ BLOG POSTS -----------------------------------")
    max_width = max((len('{:,}'.format(int(p.view_count))) for p in posts))
    for idx, p in enumerate(posts):
        padded = ' ' * (max_width - len('{:,}'.format(int(p.view_count))))
        print("{}. {} [{}{:,}]: {}".format(idx + 1, p.id, padded, int(p.view_count), p.title))
    print()


def get_posts():
    url = base_url

    with urllib.request.urlopen(url) as resp:
        if resp.getcode() != 200:
            print("Error downloading posts: {} {}".format(resp.getcode(), resp.read()))

        text = resp.read()
        post_data = json.loads(text)

        return [
            Post(**post)
            for post in post_data
            ]


def add_post():
    now = datetime.datetime.now()
    published_text = '{}-{}-{}'.format(now.year, str(now.month).zfill(2), str(now.day).zfill(2))

    title = input('title: ')
    content = input('content: ')
    view_count = int(input('view count: '))

    post_data = dict(title=title, content=content, view_count=view_count, published=published_text)
    url = base_url
    headers = {'content-type': 'application/json'}

    data = json.dumps(post_data).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        if resp.getcode() != 201:
            print("Error creating post: {} {}".format(resp.getcode(), resp.read()))
            return

        text = resp.read()

    post = json.loads(text)

    print("Created this: ")
    print(post)


def update_post():
    print("To update a post, choose the number from the list below:")
    posts = get_posts()
    show_posts(posts)
    print()

    post = posts[int(input('Enter number of post to edit: ')) - 1]

    title = input('title: [' + post.title + '] ')
    title = title if title else post.title

    content = input('content: [' + post.content + '] ')
    content = content if content else post.content

    view_count = input('view count: [' + str(post.view_count) + '] ')
    view_count = int(view_count if view_count else post.view_count)

    post_data = json.dumps(
        dict(title=title, content=content,
             view_count=view_count, published=post.published)) \
        .encode('utf-8')

    url = base_url + post.id

    req = urllib.request.Request(url, data=post_data, method='PUT')
    with urllib.request.urlopen(req) as resp:
        if resp.getcode() != 204:
            print("Error updating post: {} {}".format(resp.getcode(), resp.read()))
            return

        print("Successfully updated {}.".format(post.title))


def delete_post():
    print("To delete a post, choose the number from the list below:")
    posts = get_posts()
    show_posts(posts)
    print()

    post = posts[int(input('number of post to delete: ')) - 1]

    print("Deleting {} ...".format(post.title))

    url = base_url + post.id
    req = urllib.request.Request(url, method='DELETE')
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.getcode() != 202:
                print('Error deleting post: {} {}'.format(resp.getcode(), resp.read()))
                return

            print('Deleted {}'.format(post.title))
    except urllib.error.HTTPError as he:
        print("Error: {} {}".format(he.code, he.msg))


if __name__ == '__main__':
    main()
