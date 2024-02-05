import os
import sys

import paste.deploy
import setproctitle
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
    config.add_route('reset', '/api/reset')

    config.add_route('restricted_blog_posts', '/api/restricted/blog')
    config.add_route('restricted_blog_posts/', '/api/restricted/blog/')
    config.add_route('restricted_blog_post/post', '/api/restricted/blog/{post_id}')

    config.add_route('soap', '/soap')


def register_json_renderer(config):
    json_renderer = JSON(indent=4)
    json_renderer.add_adapter(Post, lambda p, _: p.__dict__)
    config.add_renderer('pretty_json', json_renderer)


def build_wsgi_app_if_needed():
    root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    is_prod = any(':wsgi_app' in arg for arg in sys.argv)

    if is_prod:
        config_file = os.path.join(root_folder, 'configs', 'prod-docker.ini')
        the_wsgi_app = paste.deploy.loadapp(f'config:{config_file}')
        print(f'Using server config file {config_file}')
        print(f'Command: {sys.argv}')
        setproctitle.setproctitle('granian [consuming-svcs]')
        return the_wsgi_app

    setproctitle.setproctitle('ConsumingService-Dev')
    return None


wsgi_app = build_wsgi_app_if_needed()
