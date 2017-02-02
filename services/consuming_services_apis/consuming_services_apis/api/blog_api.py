from pyramid.view import view_config
from pyramid.response import Response

from consuming_services_apis.data.memory_db import MemoryDb
from consuming_services_apis.data.post import Post

POST_LIMIT_PER_USER = 100


################################################################################
# GET /api/blog
#
@view_config(route_name='blog_posts/', renderer='pretty_json')
@view_config(route_name='blog_posts', renderer='pretty_json')
def blog_posts(request):
    print("Processing {} request from {} for the HTTP service: {}, ua: {}".format(
        request.method, get_ip(request), request.url, request.user_agent
    ))
    ip = get_ip(request)
    posts = MemoryDb.get_posts(ip)

    return posts


################################################################################
# GET /api/blog/0b52ded1-29e4-4368-a41f-5c244cb9f469
#
@view_config(route_name='blog_post/post', renderer='pretty_json', request_method='GET')
def blog_post(request):
    print("Processing {} request from {} for the HTTP service: {}, ua: {}".format(
        request.method, get_ip(request), request.url, request.user_agent
    ))

    data = build_dict(request)
    post_id = data.get('post_id')

    post = MemoryDb.get_post(post_id, get_ip(request))
    if not post:
        return Response('{"error":"Post with ID not found: ' + post_id + '"}', status=404)

    return post


################################################################################
# POST /api/blog
# { blog post data... }
#
@view_config(route_name='blog_posts', renderer='pretty_json', request_method='POST')
@view_config(route_name='blog_posts/', renderer='pretty_json', request_method='POST')
def blog_post_create(request):
    print("Processing {} request from {} for the HTTP service: {}, ua: {}".format(
        request.method, get_ip(request), request.url, request.user_agent
    ))

    all_posts = MemoryDb.get_posts(get_ip(request))
    if len(all_posts) > POST_LIMIT_PER_USER:
        MemoryDb.clear_posts(get_ip(request))
        return Response('{"error":"Too many posts created. Your blog has reset to the three default posts. '
                        'You may now add more"}', status=400)

    try:
        post_data = request.json_body
    except Exception as x:
        return Response('{"error":"Bad request '+str(x)+'"}', status=400)

    post = Post(
        post_data.get('title'),
        post_data.get('content'),
        try_int(post_data.get('view_count', 0), 0),
        post_data.get('published')
    )
    trim_post_size(post)

    MemoryDb.add_post(post, get_ip(request))
    request.response.status_code = 201

    return post


################################################################################
# PUT /api/blog
# { blog post data... }
#
@view_config(route_name='blog_post/post', renderer='pretty_json', request_method='PUT')
def update_blog_post(request):
    print("Processing {} request from {} for the HTTP service: {}, ua: {}".format(
        request.method, get_ip(request), request.url, request.user_agent
    ))

    data = build_dict(request)
    post_id = data.get('post_id')

    if MemoryDb.is_post_read_only(post_id):
        return Response('{"error":"The post with id '+str(post_id)+' is read-only. '
                        'You can only edit posts that you have created yourself via this API."}',
                        status=403)

    post = MemoryDb.get_post(post_id, get_ip(request))
    if not post:
        return Response('{"error":"Post with ID not found: ' + post_id + '"}', status=404)

    try:
        post_data = request.json_body
    except Exception as x:
        return Response('{"error":"Bad request {0}"}'.format(x), status=400)

    post.title = post_data.get('title', post.title)
    post.content = post_data.get('content', post.content)
    post.view_count = try_int(post_data.get('view_count', post.view_count), post.view_count)
    post.published = post_data.get('published', post.published)
    trim_post_size(post)

    request.response.status_code = 204

    return post


################################################################################
# DELETE /api/blog
#
@view_config(route_name='blog_post/post', renderer='pretty_json', request_method='DELETE')
def delete_blog_post(request):
    print("Processing {} request from {} for the HTTP service: {}, ua: {}".format(
        request.method, get_ip(request), request.url, request.user_agent
    ))

    data = build_dict(request)
    post_id = data.get('post_id')

    if MemoryDb.is_post_read_only(post_id):
        return Response('{"error":"The post with id '+str(post_id)+' is read-only. '
                        'You can only delete posts that you have created yourself via this API."}',
                        status=403)

    post = MemoryDb.get_post(post_id, get_ip(request))
    if not post:
        return Response('{"error":"Post with ID not found: ' + post_id + '"}', status=404)

    MemoryDb.delete_post(post, get_ip(request))
    request.response.status_code = 202

    return {'deleted': post_id}


################################################################################
# UTILITY METHODS
#

def get_ip(request):
    # The real IP is stripped by nginx and the direct request
    # looks like a call from localhost. I've configured nginx
    # to pass the IP it sees under the header X-Real-IP.
    proxy_pass_real_ip = request.headers.get('X-Real-IP')
    if proxy_pass_real_ip:
        return proxy_pass_real_ip
    elif request.remote_addr:
        return request.remote_addr
    else:
        return request.client_addr


def build_dict(request):
    data = {}
    data.update(request.GET)
    data.update(request.POST)
    data.update(request.matchdict)
    return data


# noinspection PyBroadException
def try_int(val, default: int):
    try:
        return int(val)
    except:
        return default


def trim_post_size(post):
    text_limit = 500
    if post.content and len(post.content) > text_limit:
        post.content = post.content[:500]
    if post.title and len(post.title) > text_limit:
        post.title = post.title[:500]
    if post.published and len(post.published) > text_limit:
        post.published = post.published[:500]
