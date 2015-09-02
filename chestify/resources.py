from pyramid.security import Allow, Everyone


class Root(object):
    __acl__ = [(Allow, 'principal:permitted', 'edit')]


    def __init__(self, request):
        pass