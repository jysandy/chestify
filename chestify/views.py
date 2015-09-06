import boto3
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound
from .filetree import FileTree
from .models import DBSession, User, Link

#TODO: Add view/route for directory creation


@view_config(route_name='home', renderer='templates/index.pt')
def my_view(request):
    return {'project': 'chestify'}


@view_config(route_name='list', renderer='json', request_method='GET', permission='edit')
def list_files(request):
    """ Lists the directory tree of the user in JSON format.
    """
    s3 = boto3.resource('s3')
    user = request.matchdict['user_id']
    
    #All the files of the user.
    items = [item for item in s3.Bucket('chestify').objects.all() \
                  if item.key.startswith(user)]
    
    #Update the data usage in the database.
    user_entry = DBSession.query(User).filter_by(uid=user).one()
    user_entry.data_used = sum(item.size for item in items)
    
    def remove_userid(path, userid):
        #Removes the userid prefix from a path.
        return path.replace(userid+'/', '')
    
    def get_info(s3_object):
        #Gets the size and last modified date of an S3 object.
        return {'size':s3_object.size, 'last_modified':str(s3_object.last_modified)}
    
    #Build the JSON.
    ft = FileTree()
    for item in items:
        ft.add_path(remove_userid(item.key, user), get_info(item))
    
    return ft.fs


@view_config(route_name='download-url', renderer='json', request_method='GET', request_param='key', permission='edit')
def download_url(request):
    """ Generates a presigned download URL for the given file.
    """
    client = boto3.client('s3')
    url = client.generate_presigned_url('get_object',
                                        Params={'Bucket':'chestify', 'Key':request.params['key']},
                                        ExpiresIn=30)
    return {'url':url}


@view_config(route_name='upload-url', renderer='json', request_method='GET', request_param='path', permission='edit')
def upload_url(request):
	""" Generates a presigned upload URL for the given path.
	"""
	pass


@view_config(route_name='generate-shared', renderer='json', request_method='POST', permission='edit')
def generate_shared(request):
    """ Generates a shareable link for the given file.
        Expects a form parameter called 'path'. This should be
        the full path of the file to be uploaded, EXCLUDING the
        user's ID at the beginning.
    """
    key = request.matchdict['user_id'] + '/' + request.params['path']
    
    #Check if this key exists.
    s3 = boto3.resource('s3')
    users_keys = [item.key for item in s3.Bucket('chestify').objects.all() \
                  if item.key.startswith(request.matchdict['user_id'])]
    if key not in users_keys:
        return HTTPBadRequest()
        
    link = Link(key=key)
    DBSession.add(link)
    return {'result':'success'}


@view_config(route_name='shared-download', request_method='GET')
def shared_download(request):
    """ Downloads a shared file.
    """
    try:
        link = DBSession.query(Link).filter_by(uid=request.params['id']).one()
    except NoResultFound:
        return HTTPNotFound()
    client = boto3.client('s3')
    url = client.generate_presigned_url('get_object',
                                        Params={'Bucket':'chestify', 'Key':link.key},
                                        ExpiresIn=30)
    return HTTPFound(location=url)
