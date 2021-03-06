import json
import sys
from pprint import pformat

import requests
import requests.auth

from .import sessions


FORM = 'application/x-www-form-urlencoded; charset=utf-8'
JSON = 'application/json; charset=utf-8'


def get_response(args):

    requests_kwargs = get_requests_kwargs(args)

    if args.debug:
        sys.stderr.write(
            '\n>>> requests.request(%s)\n\n' % pformat(requests_kwargs))

    if args.session:
        return sessions.get_response(args.session, requests_kwargs)
    else:
        return requests.request(**requests_kwargs)


def get_requests_kwargs(args):
    """Send the request and return a `request.Response`."""

    auto_json = args.data and not args.form
    if args.json or auto_json:
        if 'Content-Type' not in args.headers and args.data:
            args.headers['Content-Type'] = JSON

        if 'Accept' not in args.headers:
            # Default Accept to JSON as well.
            args.headers['Accept'] = 'application/json'

        if isinstance(args.data, dict):
            # If not empty, serialize the data `dict` parsed from arguments.
            # Otherwise set it to `None` avoid sending "{}".
            args.data = json.dumps(args.data) if args.data else None

    elif args.form:
        if not args.files and 'Content-Type' not in args.headers:
            # If sending files, `requests` will set
            # the `Content-Type` for us.
            args.headers['Content-Type'] = FORM

    credentials = None
    if args.auth:
        credentials = {
            'basic': requests.auth.HTTPBasicAuth,
            'digest': requests.auth.HTTPDigestAuth,
        }[args.auth_type](args.auth.key, args.auth.value)

    kwargs = {
        'prefetch': False,
        'method': args.method.lower(),
        'url': args.url,
        'headers': args.headers,
        'data': args.data,
        'verify': {
            'yes': True,
            'no': False
        }.get(args.verify,args.verify),
        'timeout': args.timeout,
        'auth': credentials,
        'proxies': dict((p.key, p.value) for p in args.proxy),
        'files': args.files,
        'allow_redirects': args.allow_redirects,
        'params': args.params
    }

    return kwargs
