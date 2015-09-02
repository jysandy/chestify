from pyramid.view import view_config


#TODO: Delete this later and replace it with our frontend
@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'chestify'}


@view_config(route_name='list', renderer='json', request_method='GET', permission='edit')
def list_files(request):
	""" Lists the directory tree of the user in JSON format.
	"""
	pass


@view_config(route_name='download-url', renderer='json', request_method='GET', request_param='key', permission='edit')
def download_url(request):
	""" Generates a presigned download URL for the given file.
	"""
	pass


@view_config(route_name='upload-url', renderer='json', request_method='GET', request_param='path', permission='edit')
def upload_url(request):
	""" Generates a presigned upload URL for the given path.
	"""
	pass


@view_config(route_name='generate-shared', renderer='json', request_method='POST', permission='edit')
def generate_shared(request):
	""" Generates a shareable link for the given file.
	"""
	pass