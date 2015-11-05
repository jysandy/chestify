from pyramid.httpexceptions import HTTPForbidden


def require_login(view_func):
    def login_check(request):
        if request.authenticated_userid is not None:
            return view_func(request)
        else:
            return HTTPForbidden()
    return login_check
