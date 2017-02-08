# import datetime
from suds.client import Client


def main():
    print("Blog explorer (SOAP/suds version)")

    print("CLIENT: ")
    print(create_client())

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


__suds_client = None


def create_client():
    global __suds_client

    if __suds_client:
        return __suds_client

    wsdl = 'http://consumer_services_api.talkpython.fm/soap?wsdl'
    __suds_client = Client(wsdl, transport=trans)

    return __suds_client


def show_posts(posts):
    if not posts:
        print("Sorry, no posts to show.")
        return

    print("------------------------------ BLOG POSTS -----------------------------------")
    max_width = max((len('{:,}'.format(int(p.ViewCount))) for p in posts))
    for idx, p in enumerate(posts):
        padded = ' ' * (max_width - len('{:,}'.format(int(p.ViewCount))))
        print("{}. {} [{}{:,}]: {}".format(idx + 1, p.Id, padded, int(p.ViewCount), p.Title))
    print()


def get_posts():
    client = create_client()
    posts = client.service.AllPosts()[0]

    return posts


def add_post():
    # now = datetime.datetime.now()
    # published_text = '{}-{}-{}'.format(now.year, str(now.month).zfill(2), str(now.day).zfill(2))

    title = input('title: ')
    content = input('content: ')
    view_count = int(input('view count: '))

    client = create_client()
    post = client.service.CreatePost(title, content, view_count)

    print("Created this: ")
    print(post)


def update_post():
    print("To update a post, choose the number from the list below:")
    posts = get_posts()
    show_posts(posts)
    print()

    post = posts[int(input('Enter number of post to edit: ')) - 1]

    title = input('title: [' + post.Title + '] ')
    title = title if title else post.Title

    content = input('content: [' + post.Content + '] ')
    content = content if content else post.Content

    view_count = input('view count: [' + str(post.ViewCount) + '] ')
    view_count = int(view_count if view_count else post.ViewCount)

    client = create_client()
    client.service.UpdatePost(post.Id, title, content, view_count)

    print("Successfully updated {}.".format(post.Title))


def delete_post():
    print("To delete a post, choose the number from the list below:")
    posts = get_posts()
    show_posts(posts)
    print()

    post = posts[int(input('number of post to delete: ')) - 1]

    print("Deleting {} ...".format(post.Title))

    client = create_client()
    client.service.DeletePost(post.Id)

    print("Deleted.")


if __name__ == '__main__':
    main()
