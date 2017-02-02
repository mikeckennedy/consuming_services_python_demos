import uuid


class Post:
    def __init__(self, title, content, view_count, published):
        self.id = str(uuid.uuid4())
        self.published = published
        self.view_count = view_count
        self.content = content
        self.title = title
