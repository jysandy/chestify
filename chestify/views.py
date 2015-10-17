import boto3
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound
from .filetree import FileTree
from .models import DBSession, User, Link
from pyramid.security import remember, forget
from pyramid.response import Response
from .utils import require_login


@view_config(route_name='home',
             renderer='templates/index.pt')
def home_view(request):
    return {'project': 'chestify'}


@view_config(route_name='list',
             renderer='json',
             request_method='GET')
@require_login
def list_files(request):
    """ Lists the directory tree of the user in JSON format.
    """
    user = request.authenticated_userid
    s3 = boto3.resource('s3')

    # All the files of the user.
    items = [item for item in s3.Bucket('chestify').objects.all()
             if item.key.startswith(user)]

    # Update the data usage in the database.
    user_entry = DBSession.query(User).filter(User.uid == user).one()
    user_entry.data_used = sum(item.size for item in items)
    
    def remove_userid(path, userid):
        # Removes the userid prefix from a path.
        return path.replace(userid+'/', '')
    
    def get_info(s3_object):
        # Gets the size and last modified date of an S3 object.
        return {'size': s3_object.size, 'last_modified': str(s3_object.last_modified)}
    
    # Build the JSON.
    ft = FileTree()
    for item in items:
        ft.add_path(remove_userid(item.key, user), get_info(item))
    
    return ft.fs


@view_config(route_name='download-url',
             renderer='json',
             request_method='GET',
             request_param='key')
@require_login
def download_url(request):
    """ Generates a presigned download URL for the given file.
    """
    user_id = request.authenticated_userid
    client = boto3.client('s3')
    url = client.generate_presigned_url('get_object',
                                        Params={'Bucket': 'chestify', 'Key': user_id + '/' + request.params['key']},
                                        ExpiresIn=30)
    return {'url': url}


@view_config(route_name='upload-url',
             renderer='json',
             request_method='GET',
             request_param='key')
@require_login
def upload_url(request):
    """ Generates a presigned upload URL for the given path.
    """
    user_id = request.authenticated_userid
    client = boto3.client('s3')
    url = client.generate_presigned_url('put_object',
                                        Params={'Bucket': 'chestify', 'Key': user_id + '/' + request.params['key']},
                                        ExpiresIn=30)
    return {'url': url}


@view_config(route_name='create-dir',
             renderer='json',
             request_method='POST')
@require_login
def create_directory(request):
    """ Creates an empty directory.
    """
    # Assuming request.params['key'] is of the form
    # foo/goo/bar/
    key = request.authenticated_userid + '/' + request.params['key'] + '.dir'
    s3 = boto3.resource('s3')
    new_dir = s3.Object(bucket_name='chestify', key=key)
    response = new_dir.put(Body=b'')
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return {'result': 'success'}
    else:
        return {'result': 'failure'}
    

@view_config(route_name='generate-shared',
             renderer='json',
             request_method='POST')
@require_login
def generate_shared(request):
    """ Generates a shareable link for the given file.
        Expects a form parameter called 'key'. This should be
        the full path of the file to be uploaded, EXCLUDING the
        user's ID at the beginning.
    """
    key = request.authenticated_userid + '/' + request.params['key']
    
    # Check if this key exists.
    s3 = boto3.resource('s3')
    users_keys = [item.key for item in s3.Bucket('chestify').objects.all()
                  if item.key.startswith(request.authenticated_userid)]
    if key not in users_keys:
        return HTTPBadRequest()
        
    link = Link(key=key)
    DBSession.add(link)
    DBSession.flush()
    DBSession.refresh(link)  # This sets link.uid to the generated primary key
    return {'result': 'success', 'link_id': link.uid}


@view_config(route_name='shared-download',
             request_method='GET',
             request_param='id')
def shared_download(request):
    """ Downloads a shared file.
    """
    try:
        link = DBSession.query(Link).filter(Link.uid == request.params['id']).one()
    except NoResultFound:
        return HTTPNotFound()
    client = boto3.client('s3')
    url = client.generate_presigned_url('get_object',
                                        Params={'Bucket': 'chestify', 'Key': link.key},
                                        ExpiresIn=30)
    return HTTPFound(location=url)


@view_config(
    route_name='login',
    request_method='POST')
def login(request):
    """ Logs in the goddamn user
    """
    from oauth2client import client, crypt
    token = request.params.get('id_token')
    id_info = client.verify_id_token(token, '687216091613-fqbv5u4cba3bpa6ihqgh8qr1h93klvap.apps.googleusercontent.com')
    userid = id_info['sub']
    headers = remember(request, userid)
    response = Response()
    response.headerlist.extend(headers)
    return response


@view_config(
    route_name='logout',
    request_method='GET')
def logout(request):
    """ Logout user throw him out 
    """
    headers = forget(request)
    response = Response()
    response.headerlist.extend(headers)
    return response
