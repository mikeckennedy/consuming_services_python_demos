import base64


def has_auth(request):
    header = request.headers.get('Authorization')
    return header is not None


def validate_auth(request):
    header = request.headers.get('Authorization')
    # expect: 'Basic a2VubmVkeTpzdXBlcl9sb2NrZG93bg==''

    if not header:
        return None

    parts = header.split(' ')
    if not len(parts) == 2:
        return False

    if not parts[0].strip().lower() == 'basic':
        return False

    val = parts[1].strip()
    return check_user_and_password(val)


def check_user_and_password(auth_val):
    user = b'kennedy'
    pw = b'super_lockdown'

    expected_bytes = base64.encodebytes(user + b':' + pw)
    expected = expected_bytes.decode('utf-8').strip()

    return auth_val == expected
