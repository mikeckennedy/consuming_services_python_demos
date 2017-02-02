from consuming_services_apis.data.post import Post


class MemoryDb:
    data_lookup = {}
    base_data = []

    @staticmethod
    def add_post(post, ip_address):
        if ip_address not in MemoryDb.data_lookup:
            MemoryDb.data_lookup[ip_address] = []

        MemoryDb.data_lookup[ip_address].append(post)

    @staticmethod
    def get_posts(ip_address):
        MemoryDb.ensure_base_data()
        posts = []
        posts.extend(MemoryDb.base_data)
        if ip_address in MemoryDb.data_lookup:
            posts.extend(MemoryDb.data_lookup[ip_address])

        posts.sort(key=lambda p: p.published)
        posts.reverse()

        return posts

    @staticmethod
    def get_post(post_id, ip_address):
        posts = MemoryDb.get_posts(ip_address)
        post_query = [p for p in posts if p.id == post_id]
        if not post_query:
            return None

        post = post_query[0]
        return post

    @staticmethod
    def is_post_read_only(post_id):
        MemoryDb.ensure_base_data()
        for p in MemoryDb.base_data:
            if p.id == post_id:
                return True

        return False

    @classmethod
    def ensure_base_data(cls):
        if MemoryDb.base_data:
            return

        post = Post(
            title="Easy Breezy Python HTTP Clients",
            published='2017-02-14',
            content="So maybe you've heard about Requests...",
            view_count=1231
        )
        post.id = 'c7081102-e2c9-41ec-8b79-adc1f3469d91'
        MemoryDb.base_data.append(post)

        post = Post(
            title="Introducing Requests for Python",
            published='2017-02-08',
            content="Python's standard urllib2 module provides most of the HTTP capabilities you need, but the API "
                    "is thoroughly broken. It was built for a different time - and a different web. It requires an "
                    "enormous amount of work (even method overrides) to perform the simplest of tasks.\n\nThings "
                    "shouldn't be this way. Not in Python.",
            view_count=10
        )
        post.id = '82160025-e50d-4993-aef7-dc423677ab05'
        MemoryDb.base_data.append(post)

        post = Post(
            title="PyCharm, the Best IDE for Python",
            published='2017-02-01',
            content="Enjoy productive Python, Django, and Web development with PyCharm, an intelligent "
                    "Python IDE offering unique coding experience...",
            view_count=100
        )
        post.id = '0b52ded1-29e4-4368-a41f-5c244cb9f469'
        MemoryDb.base_data.append(post)

    @classmethod
    def clear_posts(cls, ip_address):
        if ip_address in MemoryDb.data_lookup:
            MemoryDb.data_lookup[ip_address] = []

    @classmethod
    def delete_post(cls, post, ip_address):
        if MemoryDb.is_post_read_only(post.id):
            raise Exception("Cannot delete readonly post")

        posts = MemoryDb.data_lookup.get(ip_address, [])
        posts.remove(post)
