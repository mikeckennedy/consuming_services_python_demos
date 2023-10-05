##############################################################
# Sorry folks, suds-jurko is no longer supported and
# no longer works on supported Python versions.
# If you *must* use it (it's great when it works), please
# Use Python 3.3 to run it.
#
# We'll use zeep instead: https://docs.python-zeep.org/en/master/
#
import zeep


def main():
    print("Blog explorer (SOAP/zeep version)")

    print("CLIENT: ")
    print(create_client())

    while True:
        action = input('What to do with this blog api? [l]ist, [a]dd, [u]pdate, [d]elete, e[x]it: ')  # noqa
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


__zeep_client = None


def create_client():
    global __zeep_client

    if __zeep_client:
        return __zeep_client

    wsdl = 'https://consumerservicesapi.talkpython.fm/soap?wsdl'
    __zeep_client = zeep.Client(wsdl=wsdl)

    return __zeep_client


def show_posts(posts):
    if not posts:
        print("Sorry, no posts to show.")
        return

    print("------------------------------ BLOG POSTS -----------------------------------")  # noqa
    max_width = max((len('{:,}'.format(int(p.ViewCount))) for p in posts))
    for idx, p in enumerate(posts):
        padded = ' ' * (max_width - len('{:,}'.format(int(p.ViewCount))))
        print("{}. {} [{}{:,}]: {}".format(idx + 1, p.Id, padded, int(p.ViewCount), p.Title))  # noqa
    print()


def get_posts():
    client = create_client()
    posts = client.service.AllPosts()
    print(type(posts), posts)

    return posts


def add_post():
    title = input('title: ')
    content = input('content: ')
    view_count = int(input('view count: '))

    client = create_client()
    post = client.service.CreatePost(title=title, content=content, viewCount=view_count)

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
