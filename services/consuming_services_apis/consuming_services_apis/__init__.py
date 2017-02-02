from pyramid.config import Configurator
from pyramid.renderers import JSON

from consuming_services_apis.data.post import Post


def main(_, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    register_includes(config)
    register_json_renderer(config)
    register_routes(config)

    config.scan()
    return config.make_wsgi_app()


def register_includes(config):
    config.include('pyramid_chameleon')


def register_routes(config):
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')

    config.add_route('blog_posts', '/api/blog')
    config.add_route('blog_posts/', '/api/blog/')
    config.add_route('blog_post/post', '/api/blog/{post_id}')

    config.add_route('restricted_blog_posts', '/api/restricted/blog')
    config.add_route('restricted_blog_posts/', '/api/restricted/blog/')
    config.add_route('restricted_blog_post/post', '/api/restricted/blog/{post_id}')

    config.add_route('soap', '/soap')


def register_json_renderer(config):
    json_renderer = JSON(indent=4)
    json_renderer.add_adapter(Post, lambda p, _: p.__dict__)
    config.add_renderer('pretty_json', json_renderer)
