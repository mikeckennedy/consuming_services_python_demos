from pyramid.view import view_config
from pyramid.response import Response

from .blog_api import blog_post as raw_blog_post
from .blog_api import blog_posts as raw_blog_posts
from .blog_api import blog_post_create as raw_blog_post_create
from .blog_api import update_blog_post as raw_update_blog_post
from .blog_api import delete_blog_post as raw_delete_blog_post

from consuming_services_apis.infrastructure import auth_service


################################################################################
# GET /api/restricted/blog
#
@view_config(route_name='restricted_blog_posts/', renderer='pretty_json')
@view_config(route_name='restricted_blog_posts', renderer='pretty_json')
def blog_posts(request):
    error_response = validate_auth_and_generate_failed_response(request)
    if error_response:
        return error_response

    return raw_blog_posts(request)


################################################################################
# GET /api/restricted/blog/0b52ded1-29e4-4368-a41f-5c244cb9f469
#
@view_config(route_name='restricted_blog_post/post', renderer='pretty_json', request_method='GET')
def blog_post(request):
    error_response = validate_auth_and_generate_failed_response(request)
    if error_response:
        return error_response

    return raw_blog_post(request)


################################################################################
# POST /api/restricted/blog
# { blog post data... }
#
@view_config(route_name='restricted_blog_posts', renderer='pretty_json', request_method='POST')
@view_config(route_name='restricted_blog_posts/', renderer='pretty_json', request_method='POST')
def blog_post_create(request):
    error_response = validate_auth_and_generate_failed_response(request)
    if error_response:
        return error_response

    return raw_blog_post_create(request)


################################################################################
# PUT /api/restricted/blog
# { blog post data... }
#
@view_config(route_name='restricted_blog_post/post', renderer='pretty_json', request_method='PUT')
def update_blog_post(request):
    error_response = validate_auth_and_generate_failed_response(request)
    if error_response:
        return error_response

    return raw_update_blog_post(request)


################################################################################
# DELETE /api/blog
#
@view_config(route_name='restricted_blog_post/post', renderer='pretty_json', request_method='DELETE')
def delete_blog_post(request):
    error_response = validate_auth_and_generate_failed_response(request)
    if error_response:
        return error_response

    return raw_delete_blog_post(request)


def validate_auth_and_generate_failed_response(request):
    if not auth_service.has_auth(request):
        response = Response("You must authenticate using basic auth (username, password) to access this service.",
                            status=401)
        response.headers.add("WWW-Authenticate", "Basic realm=\"None\"")
        return response

    if not auth_service.validate_auth(request):
        return Response("Invalid username or password.", status=403)

    return None
